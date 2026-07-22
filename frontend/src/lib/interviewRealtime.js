import { CONNECTION_STATUS } from './interviewTypes';
import { createRealtimeEventSequencer } from './realtimeEventSequencer';

const OPENAI_REALTIME_CALLS_URL = 'https://api.openai.com/v1/realtime/calls';
const DEFAULT_RECONNECT_ATTEMPTS = 3;
const DEFAULT_RECONNECT_BASE_DELAY_MS = 1_000;
const DEFAULT_RECONNECT_MAX_DELAY_MS = 300_000;

function nowIso() {
  return new Date().toISOString();
}

function transcriptKey(event) {
  return event.response_id || event.item_id || event.output_index || 'assistant';
}

function retryAfterMilliseconds(error, maximumDelayMs) {
  const headers = error?.response?.headers;
  const rawValue = headers?.get?.('retry-after')
    ?? headers?.['retry-after']
    ?? error?.response?.data?.retry_after_seconds;
  const seconds = Number(rawValue);
  if (!Number.isFinite(seconds) || seconds < 0) return null;
  return Math.min(Math.ceil(seconds * 1000), maximumDelayMs);
}

function abortError() {
  const error = new Error('Realtime reconnect was cancelled');
  error.name = 'AbortError';
  return error;
}

function waitForDelay(milliseconds, signal, setTimer, clearTimer) {
  if (signal.aborted) return Promise.reject(abortError());
  return new Promise((resolve, reject) => {
    const timer = setTimer(() => {
      signal.removeEventListener('abort', onAbort);
      resolve();
    }, milliseconds);
    function onAbort() {
      clearTimer(timer);
      signal.removeEventListener('abort', onAbort);
      reject(abortError());
    }
    signal.addEventListener('abort', onAbort, { once: true });
  });
}

function publicConnectionError(error) {
  if (error?.name === 'NotAllowedError') {
    return 'Quyền microphone đã bị từ chối.';
  }
  if (error?.code === 'EVENT_SYNC_FAILED') {
    return 'Không thể đồng bộ bản ghi phiên. Vui lòng thử kết nối lại.';
  }
  if (error?.response?.status === 503) {
    return 'Phỏng vấn bằng giọng nói hiện chưa được cấu hình.';
  }
  return 'Không thể kết nối phỏng vấn bằng giọng nói. Vui lòng thử lại.';
}

/**
 * Low-level OpenAI Realtime WebRTC controller. The long-lived provider key is
 * never available here; the short-lived credential is used once for SDP and
 * kept only in this connect() stack frame.
 */
export function createRealtimeSession({
  sessionId,
  mediaStream,
  questionLimit = 5,
  createClientSecret,
  sendAuditEvent,
  fetchImpl = globalThis.fetch,
  RTCPeerConnectionImpl = globalThis.RTCPeerConnection,
  audioElementFactory = () => document.createElement('audio'),
  isOnline = () => globalThis.navigator?.onLine !== false,
  maxReconnectAttempts = DEFAULT_RECONNECT_ATTEMPTS,
  reconnectBaseDelayMs = DEFAULT_RECONNECT_BASE_DELAY_MS,
  reconnectMaxDelayMs = DEFAULT_RECONNECT_MAX_DELAY_MS,
  setTimer = globalThis.setTimeout,
  clearTimer = globalThis.clearTimeout,
}) {
  if (!sessionId) throw new TypeError('sessionId is required');
  if (!mediaStream?.getAudioTracks?.().length) {
    throw new TypeError('A consented microphone stream is required');
  }
  if (typeof createClientSecret !== 'function' || typeof sendAuditEvent !== 'function') {
    throw new TypeError('Realtime backend functions are required');
  }

  const listeners = {
    stateChange: [],
    transcript: [],
    aiSpeaking: [],
    userSpeaking: [],
    processing: [],
    turnsChange: [],
    error: [],
  };
  const sequencer = createRealtimeEventSequencer(sendAuditEvent);

  let status = CONNECTION_STATUS.IDLE;
  let peerConnection = null;
  let dataChannel = null;
  let remoteAudio = null;
  let providerSessionId = null;
  let transcript = [];
  let turns = [];
  let assistantDeltas = new Map();
  let transcriptCounter = 0;
  let connectPromise = null;
  let reconnectPromise = null;
  let reconnectController = null;
  let destroyed = false;
  let ended = false;
  let hasConnectedOnce = false;

  function emit(event, value) {
    (listeners[event] || []).forEach((listener) => listener(value));
  }

  function setStatus(nextStatus) {
    status = nextStatus;
    emit('stateChange', nextStatus);
  }

  function addTranscript(speaker, text, providerItemId) {
    const normalized = String(text || '').trim();
    if (!normalized) return null;
    const entry = {
      id: providerItemId || `transcript-${++transcriptCounter}`,
      speaker,
      text: normalized,
      timestamp: Date.now(),
    };
    const previous = transcript[transcript.length - 1];
    const isDuplicate = transcript.some(
      (item) => item.id === entry.id && item.text === entry.text
    ) || (previous?.speaker === speaker && previous?.text === normalized);
    if (isDuplicate) return null;
    transcript = [...transcript, entry];
    emit('transcript', entry);
    return entry;
  }

  function enqueueAudit(eventType, payload) {
    return sequencer.enqueue(eventType, payload).catch((cause) => {
      const error = new Error('Realtime audit event synchronization failed', { cause });
      const responseStatus = cause?.response?.status;
      error.code = responseStatus === 409 ? 'EVENT_SEQUENCE_CONFLICT' : 'EVENT_SYNC_FAILED';
      emit('error', {
        code: error.code,
        message: responseStatus === 409
          ? 'Chuỗi sự kiện phỏng vấn không còn đồng bộ. Hãy kết thúc phiên và tạo phiên mới.'
          : publicConnectionError(error),
        retryable: responseStatus !== 409 && responseStatus !== 422,
      });
      return null;
    });
  }

  function appendQuestion(text, providerItemId) {
    if (turns.length >= questionLimit) return;
    const turnIndex = turns.length;
    const occurredAt = nowIso();
    const turn = {
      turn_index: turnIndex,
      question_text: text,
      question_type: null,
      answer_transcript: null,
      ai_followup_text: null,
      started_at: occurredAt,
      ended_at: null,
    };
    turns = [...turns, turn];
    emit('turnsChange', [...turns]);
    void enqueueAudit('question_started', {
      turn_index: turnIndex,
      question_text: text,
      occurred_at: occurredAt,
    });
    void enqueueAudit('assistant_transcript_completed', {
      turn_index: turnIndex,
      transcript: text,
      transcript_kind: 'question',
      ...(providerItemId ? { provider_item_id: providerItemId } : {}),
      occurred_at: occurredAt,
    });
  }

  function appendAnswer(text, providerItemId) {
    const turnIndex = turns.length - 1;
    if (turnIndex < 0) return;
    const occurredAt = nowIso();
    turns = turns.map((turn, index) =>
      index === turnIndex
        ? { ...turn, answer_transcript: text, ended_at: occurredAt }
        : turn
    );
    emit('turnsChange', [...turns]);
    void enqueueAudit('user_transcript_completed', {
      turn_index: turnIndex,
      transcript: text,
      ...(providerItemId ? { provider_item_id: providerItemId } : {}),
      occurred_at: occurredAt,
    });
    void enqueueAudit('question_completed', {
      turn_index: turnIndex,
      question_text: turns[turnIndex].question_text,
      occurred_at: occurredAt,
    });
  }

  function handleProviderEvent(event) {
    if (!event || typeof event.type !== 'string') return;

    switch (event.type) {
      case 'session.created':
        providerSessionId = event.session?.id || providerSessionId;
        break;
      case 'input_audio_buffer.speech_started':
        emit('userSpeaking', true);
        emit('processing', false);
        break;
      case 'input_audio_buffer.speech_stopped':
        emit('userSpeaking', false);
        emit('processing', true);
        break;
      case 'conversation.item.input_audio_transcription.completed': {
        const entry = addTranscript('user', event.transcript, event.item_id);
        if (entry) appendAnswer(entry.text, event.item_id);
        break;
      }
      case 'response.output_audio_transcript.delta':
      case 'response.audio_transcript.delta': {
        const key = transcriptKey(event);
        assistantDeltas.set(key, `${assistantDeltas.get(key) || ''}${event.delta || ''}`);
        emit('aiSpeaking', true);
        emit('processing', false);
        break;
      }
      case 'response.output_audio_transcript.done':
      case 'response.audio_transcript.done': {
        const key = transcriptKey(event);
        const text = event.transcript || assistantDeltas.get(key) || '';
        assistantDeltas.delete(key);
        const entry = addTranscript('ai', text, event.item_id || key);
        if (entry) appendQuestion(entry.text, event.item_id);
        emit('aiSpeaking', false);
        break;
      }
      case 'response.created':
        emit('processing', true);
        break;
      case 'response.output_audio.delta':
      case 'response.audio.delta':
        emit('aiSpeaking', true);
        emit('processing', false);
        break;
      case 'response.output_audio.done':
      case 'response.audio.done':
      case 'response.done':
        emit('aiSpeaking', false);
        emit('processing', false);
        break;
      case 'error':
        emit('error', {
          code: 'PROVIDER_EVENT_ERROR',
          message: 'Dịch vụ phỏng vấn gặp lỗi. Vui lòng kết nối lại.',
          retryable: true,
        });
        break;
      default:
        break;
    }
  }

  function usableAudioTracks() {
    return mediaStream.getAudioTracks().filter((track) => track.readyState !== 'ended');
  }

  function closeTransport() {
    const channel = dataChannel;
    const connection = peerConnection;
    const audio = remoteAudio;
    dataChannel = null;
    peerConnection = null;
    remoteAudio = null;
    if (connection) {
      connection.ontrack = null;
      connection.onconnectionstatechange = null;
    }
    channel?.close();
    connection?.close();
    if (audio) {
      audio.srcObject = null;
    }
  }

  async function connect({ reconnecting = false, reportError = true, signal = null } = {}) {
    if (destroyed) throw new Error('Realtime session has been destroyed');
    if (ended) throw new Error('Realtime session has ended');
    if (status === CONNECTION_STATUS.CONNECTED) return;
    if (connectPromise) return connectPromise;

    connectPromise = (async () => {
      setStatus(reconnecting ? CONNECTION_STATUS.RECONNECTING : CONNECTION_STATUS.CONNECTING);
      let credential = null;
      try {
        if (!isOnline()) {
          const error = new Error('Browser is offline');
          error.code = 'NETWORK_OFFLINE';
          throw error;
        }
        const audioTracks = usableAudioTracks();
        if (!audioTracks.length) {
          const error = new Error('Microphone permission is no longer available');
          error.name = 'NotAllowedError';
          error.code = 'MICROPHONE_UNAVAILABLE';
          throw error;
        }
        credential = await createClientSecret(sessionId);
        if (signal?.aborted || ended || destroyed) throw abortError();
        const ephemeralKey = credential?.client_secret;
        if (!ephemeralKey) throw new Error('Missing ephemeral credential');
        if (typeof RTCPeerConnectionImpl !== 'function') {
          throw new Error('WebRTC is not supported');
        }

        providerSessionId = credential.provider_session_id || null;
        const nextPeerConnection = new RTCPeerConnectionImpl();
        peerConnection = nextPeerConnection;
        remoteAudio = audioElementFactory();
        remoteAudio.autoplay = true;
        remoteAudio.playsInline = true;

        nextPeerConnection.ontrack = (event) => {
          if (peerConnection !== nextPeerConnection) return;
          remoteAudio.srcObject = event.streams?.[0] || null;
        };
        nextPeerConnection.onconnectionstatechange = () => {
          if (peerConnection !== nextPeerConnection || ended || destroyed) return;
          const connectionState = nextPeerConnection.connectionState;
          if (connectionState === 'failed') {
            setStatus(CONNECTION_STATUS.FAILED);
            emit('error', {
              code: 'WEBRTC_CONNECTION_FAILED',
              message: 'Kết nối WebRTC đã bị gián đoạn.',
              retryable: true,
            });
          } else if (connectionState === 'disconnected') {
            setStatus(CONNECTION_STATUS.DISCONNECTED);
            emit('error', {
              code: 'WEBRTC_CONNECTION_DISCONNECTED',
              message: 'Kết nối mạng bị gián đoạn. Bạn có thể kết nối lại an toàn.',
              retryable: true,
            });
          }
        };

        audioTracks.forEach((track) => {
          nextPeerConnection.addTrack(track, mediaStream);
        });

        const nextDataChannel = nextPeerConnection.createDataChannel('oai-events');
        dataChannel = nextDataChannel;
        nextDataChannel.addEventListener('message', (message) => {
          try {
            handleProviderEvent(JSON.parse(message.data));
          } catch {
            emit('error', {
              code: 'INVALID_PROVIDER_EVENT',
              message: 'Dữ liệu thời gian thực không hợp lệ đã được bỏ qua.',
              retryable: false,
            });
          }
        });
        nextDataChannel.addEventListener('close', () => {
          if (dataChannel !== nextDataChannel || ended || destroyed) return;
          setStatus(CONNECTION_STATUS.DISCONNECTED);
          emit('error', {
            code: 'WEBRTC_DATA_CHANNEL_CLOSED',
            message: 'Kênh dữ liệu thời gian thực đã đóng ngoài dự kiến.',
            retryable: true,
          });
        });
        nextDataChannel.addEventListener('open', () => {
          if (dataChannel !== nextDataChannel || ended || destroyed) return;
          setStatus(CONNECTION_STATUS.CONNECTED);
          void enqueueAudit('session_connected', {
            ...(providerSessionId ? { provider_session_id: providerSessionId } : {}),
            transport: 'webrtc',
            occurred_at: nowIso(),
          });
          if (!hasConnectedOnce || turns.length === 0) {
            nextDataChannel.send(JSON.stringify({ type: 'response.create' }));
          }
          hasConnectedOnce = true;
        });

        const offer = await nextPeerConnection.createOffer();
        await nextPeerConnection.setLocalDescription(offer);
        const response = await fetchImpl(OPENAI_REALTIME_CALLS_URL, {
          method: 'POST',
          body: offer.sdp,
          headers: {
            Authorization: `Bearer ${ephemeralKey}`,
            'Content-Type': 'application/sdp',
          },
        });
        if (signal?.aborted || ended || destroyed) throw abortError();
        if (!response.ok) throw new Error('OpenAI WebRTC negotiation failed');
        await nextPeerConnection.setRemoteDescription({
          type: 'answer',
          sdp: await response.text(),
        });
      } catch (error) {
        closeTransport();
        if (!reconnecting) setStatus(CONNECTION_STATUS.FAILED);
        if (reportError) {
          emit('error', {
            code: error?.code || 'WEBRTC_CONNECT_FAILED',
            message: publicConnectionError(error),
            retryable: error?.code !== 'MICROPHONE_UNAVAILABLE',
          });
        }
        throw error;
      } finally {
        credential = null;
        connectPromise = null;
      }
    })();

    return connectPromise;
  }

  async function disconnect(reason = 'user_ended') {
    if (reason === 'user_ended' || reason === 'component_unmounted') {
      ended = true;
      reconnectController?.abort();
    }
    try {
      closeTransport();
    } finally {
      emit('aiSpeaking', false);
      emit('userSpeaking', false);
      emit('processing', false);
      if (status !== CONNECTION_STATUS.IDLE) {
        setStatus(CONNECTION_STATUS.DISCONNECTED);
        try {
          await enqueueAudit('session_disconnected', {
            reason,
            occurred_at: nowIso(),
          });
        } catch {
          // The pending event remains available for an exact retry.
        }
      }
    }
  }

  const session = {
    on(event, listener) {
      if (listeners[event]) listeners[event].push(listener);
      return session;
    },
    off(event, listener) {
      if (listeners[event]) {
        listeners[event] = listeners[event].filter((item) => item !== listener);
      }
      return session;
    },
    connect,
    disconnect,
    async reconnect() {
      if (destroyed || ended) return false;
      if (reconnectPromise) return reconnectPromise;
      reconnectController = new AbortController();
      const { signal } = reconnectController;
      reconnectPromise = (async () => {
        closeTransport();
        emit('aiSpeaking', false);
        emit('userSpeaking', false);
        emit('processing', false);
        setStatus(CONNECTION_STATUS.RECONNECTING);
        await enqueueAudit('session_disconnected', {
          reason: 'network_interrupted',
          occurred_at: nowIso(),
        });

        let lastError = null;
        for (let attempt = 0; attempt < maxReconnectAttempts; attempt += 1) {
          if (signal.aborted) return false;
          if (attempt > 0 && lastError?.response?.status !== 409) {
            const delay = Math.min(
              reconnectBaseDelayMs * (2 ** (attempt - 1)),
              reconnectMaxDelayMs,
            );
            await waitForDelay(delay, signal, setTimer, clearTimer);
          }
          try {
            await connect({ reconnecting: true, reportError: false, signal });
            return true;
          } catch (error) {
            lastError = error;
            if (signal.aborted) return false;
            if (error?.code === 'MICROPHONE_UNAVAILABLE' || error?.name === 'NotAllowedError') {
              setStatus(CONNECTION_STATUS.FAILED);
              emit('error', {
                code: 'MICROPHONE_UNAVAILABLE',
                message: 'Quyền microphone không còn hiệu lực. Hãy cấp quyền lại trước khi kết nối.',
                retryable: false,
              });
              throw error;
            }

            const retryAfterMs = error?.response?.status === 409
              ? retryAfterMilliseconds(error, reconnectMaxDelayMs)
              : null;
            const canRetry = attempt + 1 < maxReconnectAttempts
              && (error?.response?.status !== 409 || retryAfterMs !== null);
            if (!canRetry) {
              setStatus(CONNECTION_STATUS.FAILED);
              emit('error', {
                code: 'WEBRTC_RECONNECT_FAILED',
                message: publicConnectionError(error),
                retryable: true,
              });
              throw error;
            }

            setStatus(CONNECTION_STATUS.RECONNECTING);
            if (retryAfterMs !== null) {
              emit('error', {
                code: 'RECONNECT_THROTTLED',
                message: `Máy chủ yêu cầu chờ ${Math.ceil(retryAfterMs / 1000)} giây trước khi kết nối lại.`,
                retryable: true,
                retryAfterSeconds: Math.ceil(retryAfterMs / 1000),
              });
              await waitForDelay(retryAfterMs, signal, setTimer, clearTimer);
            } else if (!isOnline()) {
              emit('error', {
                code: 'NETWORK_OFFLINE',
                message: 'Thiết bị đang ngoại tuyến. Hệ thống sẽ thử lại có giới hạn.',
                retryable: true,
              });
            }
          }
        }
        return false;
      })().catch((error) => {
        if (error?.name === 'AbortError') return false;
        throw error;
      }).finally(() => {
        reconnectPromise = null;
        reconnectController = null;
      });
      return reconnectPromise;
    },
    cancelReconnect() {
      reconnectController?.abort();
      closeTransport();
      if (!ended && !destroyed) setStatus(CONNECTION_STATUS.DISCONNECTED);
    },
    retryPendingEvent() {
      return sequencer.retryPending();
    },
    getState() {
      return {
        status,
        transcript: [...transcript],
        turns: turns.map((turn) => ({ ...turn })),
      };
    },
    async destroy() {
      destroyed = true;
      await disconnect('component_unmounted');
      Object.keys(listeners).forEach((key) => {
        listeners[key] = [];
      });
    },
  };

  return session;
}
