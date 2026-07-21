import { CONNECTION_STATUS } from './interviewTypes';
import { createRealtimeEventSequencer } from './realtimeEventSequencer';

const OPENAI_REALTIME_CALLS_URL = 'https://api.openai.com/v1/realtime/calls';

function nowIso() {
  return new Date().toISOString();
}

function transcriptKey(event) {
  return event.response_id || event.item_id || event.output_index || 'assistant';
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
  let destroyed = false;

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
    if (!transcript.some((item) => item.id === entry.id && item.text === entry.text)) {
      transcript = [...transcript, entry];
      emit('transcript', entry);
    }
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

  async function connect() {
    if (destroyed) throw new Error('Realtime session has been destroyed');
    if (status === CONNECTION_STATUS.CONNECTED) return;
    if (connectPromise) return connectPromise;

    connectPromise = (async () => {
      setStatus(CONNECTION_STATUS.CONNECTING);
      let credential = null;
      try {
        credential = await createClientSecret(sessionId);
        const ephemeralKey = credential?.client_secret;
        if (!ephemeralKey) throw new Error('Missing ephemeral credential');
        if (typeof RTCPeerConnectionImpl !== 'function') {
          throw new Error('WebRTC is not supported');
        }

        providerSessionId = credential.provider_session_id || null;
        peerConnection = new RTCPeerConnectionImpl();
        remoteAudio = audioElementFactory();
        remoteAudio.autoplay = true;
        remoteAudio.playsInline = true;

        peerConnection.ontrack = (event) => {
          remoteAudio.srcObject = event.streams?.[0] || null;
        };
        peerConnection.onconnectionstatechange = () => {
          const connectionState = peerConnection?.connectionState;
          if (connectionState === 'failed') {
            setStatus(CONNECTION_STATUS.FAILED);
            emit('error', {
              code: 'WEBRTC_CONNECTION_FAILED',
              message: 'Kết nối WebRTC đã bị gián đoạn.',
              retryable: true,
            });
          } else if (connectionState === 'disconnected') {
            setStatus(CONNECTION_STATUS.DISCONNECTED);
          }
        };

        mediaStream.getAudioTracks().forEach((track) => {
          peerConnection.addTrack(track, mediaStream);
        });

        dataChannel = peerConnection.createDataChannel('oai-events');
        dataChannel.addEventListener('message', (message) => {
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
        dataChannel.addEventListener('open', () => {
          setStatus(CONNECTION_STATUS.CONNECTED);
          void enqueueAudit('session_connected', {
            ...(providerSessionId ? { provider_session_id: providerSessionId } : {}),
            transport: 'webrtc',
            occurred_at: nowIso(),
          });
          dataChannel.send(JSON.stringify({ type: 'response.create' }));
        });

        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        const response = await fetchImpl(OPENAI_REALTIME_CALLS_URL, {
          method: 'POST',
          body: offer.sdp,
          headers: {
            Authorization: `Bearer ${ephemeralKey}`,
            'Content-Type': 'application/sdp',
          },
        });
        if (!response.ok) throw new Error('OpenAI WebRTC negotiation failed');
        await peerConnection.setRemoteDescription({
          type: 'answer',
          sdp: await response.text(),
        });
      } catch (error) {
        dataChannel?.close();
        peerConnection?.close();
        if (remoteAudio) remoteAudio.srcObject = null;
        dataChannel = null;
        peerConnection = null;
        remoteAudio = null;
        setStatus(CONNECTION_STATUS.FAILED);
        emit('error', {
          code: 'WEBRTC_CONNECT_FAILED',
          message: publicConnectionError(error),
          retryable: true,
        });
        throw error;
      } finally {
        credential = null;
        connectPromise = null;
      }
    })();

    return connectPromise;
  }

  async function disconnect(reason = 'user_ended') {
    try {
      dataChannel?.close();
      peerConnection?.close();
      if (remoteAudio) remoteAudio.srcObject = null;
    } finally {
      dataChannel = null;
      peerConnection = null;
      remoteAudio = null;
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
      setStatus(CONNECTION_STATUS.RECONNECTING);
      await disconnect('network_interrupted');
      return connect();
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
