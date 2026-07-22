import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createRealtimeSession } from './interviewRealtime';

class FakeDataChannel extends EventTarget {
  constructor() {
    super();
    this.sent = [];
    this.close = vi.fn();
  }

  send(value) {
    this.sent.push(JSON.parse(value));
  }

  providerEvent(value) {
    this.dispatchEvent(new MessageEvent('message', { data: JSON.stringify(value) }));
  }
}

class FakePeerConnection {
  static instances = [];

  constructor() {
    this.channel = new FakeDataChannel();
    this.addTrack = vi.fn();
    this.close = vi.fn();
    this.createOffer = vi.fn().mockResolvedValue({ type: 'offer', sdp: 'local-sdp' });
    this.setLocalDescription = vi.fn().mockResolvedValue(undefined);
    this.setRemoteDescription = vi.fn().mockResolvedValue(undefined);
    this.connectionState = 'new';
    FakePeerConnection.instances.push(this);
  }

  createDataChannel() {
    return this.channel;
  }
}

const track = { enabled: true, readyState: 'live' };
const mediaStream = { getAudioTracks: () => [track] };

describe('OpenAI Realtime WebRTC controller', () => {
  beforeEach(() => {
    FakePeerConnection.instances = [];
    track.readyState = 'live';
    localStorage.clear();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('requires a consented microphone before requesting a client secret', () => {
    const createClientSecret = vi.fn();
    expect(() => createRealtimeSession({
      sessionId: 'session-1',
      mediaStream: null,
      createClientSecret,
      sendAuditEvent: vi.fn(),
    })).toThrow('consented microphone');
    expect(createClientSecret).not.toHaveBeenCalled();
  });

  it('uses the ephemeral credential only for SDP and renders provider transcripts', async () => {
    const createClientSecret = vi.fn().mockResolvedValue({
      client_secret: 'ek_memory_only',
      provider_session_id: 'provider-1',
    });
    const sendAuditEvent = vi.fn().mockResolvedValue({ accepted: true });
    const fetchImpl = vi.fn().mockResolvedValue({ ok: true, text: async () => 'remote-sdp' });
    const audio = { autoplay: false, playsInline: false, srcObject: null };
    const setItem = vi.spyOn(Storage.prototype, 'setItem');
    const session = createRealtimeSession({
      sessionId: 'session-1',
      mediaStream,
      createClientSecret,
      sendAuditEvent,
      fetchImpl,
      RTCPeerConnectionImpl: FakePeerConnection,
      audioElementFactory: () => audio,
    });
    const transcripts = [];
    session.on('transcript', (entry) => transcripts.push(entry));

    await session.connect();
    const pc = FakePeerConnection.instances[0];
    pc.channel.dispatchEvent(new Event('open'));
    pc.channel.providerEvent({
      type: 'response.output_audio_transcript.done',
      item_id: 'ai-1',
      transcript: 'Hãy giới thiệu một dự án kỹ thuật mà bạn tự hào.',
    });
    pc.channel.providerEvent({
      type: 'conversation.item.input_audio_transcription.completed',
      item_id: 'user-1',
      transcript: 'Tôi đã xây dựng một API bằng FastAPI.',
    });
    await Promise.resolve();
    await Promise.resolve();

    expect(fetchImpl).toHaveBeenCalledWith(
      'https://api.openai.com/v1/realtime/calls',
      expect.objectContaining({
        body: 'local-sdp',
        headers: expect.objectContaining({ Authorization: 'Bearer ek_memory_only' }),
      })
    );
    expect(pc.addTrack).toHaveBeenCalledWith(track, mediaStream);
    expect(pc.channel.sent).toContainEqual({ type: 'response.create' });
    expect(transcripts.map((entry) => entry.text)).toEqual([
      'Hãy giới thiệu một dự án kỹ thuật mà bạn tự hào.',
      'Tôi đã xây dựng một API bằng FastAPI.',
    ]);
    expect(session.getState().turns[0]).toEqual(expect.objectContaining({
      question_text: 'Hãy giới thiệu một dự án kỹ thuật mà bạn tự hào.',
      answer_transcript: 'Tôi đã xây dựng một API bằng FastAPI.',
    }));
    expect(setItem).not.toHaveBeenCalled();
    expect(JSON.stringify(sendAuditEvent.mock.calls)).not.toContain('ek_memory_only');
  });

  it('closes WebRTC resources and exposes a Vietnamese configuration error', async () => {
    const errorListener = vi.fn();
    const backendError = Object.assign(new Error('disabled'), { response: { status: 503 } });
    const session = createRealtimeSession({
      sessionId: 'session-1',
      mediaStream,
      createClientSecret: vi.fn().mockRejectedValue(backendError),
      sendAuditEvent: vi.fn(),
      fetchImpl: vi.fn(),
      RTCPeerConnectionImpl: FakePeerConnection,
    });
    session.on('error', errorListener);

    await expect(session.connect()).rejects.toThrow('disabled');

    expect(errorListener).toHaveBeenCalledWith(expect.objectContaining({
      message: 'Phỏng vấn bằng giọng nói hiện chưa được cấu hình.',
    }));
  });

  it('surfaces a sequence conflict without blindly retrying it', async () => {
    const conflict = Object.assign(new Error('conflict'), { response: { status: 409 } });
    const errorListener = vi.fn();
    const session = createRealtimeSession({
      sessionId: 'session-1',
      mediaStream,
      createClientSecret: vi.fn().mockResolvedValue({ client_secret: 'ek_memory_only' }),
      sendAuditEvent: vi.fn().mockRejectedValue(conflict),
      fetchImpl: vi.fn().mockResolvedValue({ ok: true, text: async () => 'remote-sdp' }),
      RTCPeerConnectionImpl: FakePeerConnection,
    });
    session.on('error', errorListener);

    await session.connect();
    FakePeerConnection.instances[0].channel.dispatchEvent(new Event('open'));

    await vi.waitFor(() => {
      expect(errorListener).toHaveBeenCalledWith(expect.objectContaining({
        code: 'EVENT_SEQUENCE_CONFLICT',
        retryable: false,
        message: expect.stringContaining('không còn đồng bộ'),
      }));
    });
  });

  it('honors Retry-After before minting a new credential and then reconnects', async () => {
    vi.useFakeTimers();
    const throttle = Object.assign(new Error('too recent'), {
      response: { status: 409, headers: { 'retry-after': '30' } },
    });
    const createClientSecret = vi.fn()
      .mockResolvedValueOnce({ client_secret: 'ek_initial' })
      .mockRejectedValueOnce(throttle)
      .mockResolvedValueOnce({ client_secret: 'ek_reconnected' });
    const session = createRealtimeSession({
      sessionId: 'session-1',
      mediaStream,
      createClientSecret,
      sendAuditEvent: vi.fn().mockResolvedValue({ accepted: true }),
      fetchImpl: vi.fn().mockResolvedValue({ ok: true, text: async () => 'remote-sdp' }),
      RTCPeerConnectionImpl: FakePeerConnection,
    });

    await session.connect();
    FakePeerConnection.instances[0].channel.dispatchEvent(new Event('open'));
    const reconnecting = session.reconnect();
    await vi.advanceTimersByTimeAsync(0);

    expect(createClientSecret).toHaveBeenCalledTimes(2);
    expect(session.getState().status).toBe('reconnecting');
    await vi.advanceTimersByTimeAsync(29_999);
    expect(createClientSecret).toHaveBeenCalledTimes(2);
    await vi.advanceTimersByTimeAsync(1);
    await expect(reconnecting).resolves.toBe(true);
    expect(createClientSecret).toHaveBeenCalledTimes(3);
    FakePeerConnection.instances[1].channel.dispatchEvent(new Event('open'));
    expect(session.getState().status).toBe('connected');
  });

  it('cancels a throttled reconnect without another secret request', async () => {
    vi.useFakeTimers();
    const throttle = Object.assign(new Error('too recent'), {
      response: { status: 409, headers: { 'retry-after': '30' } },
    });
    const createClientSecret = vi.fn()
      .mockResolvedValueOnce({ client_secret: 'ek_initial' })
      .mockRejectedValueOnce(throttle);
    const session = createRealtimeSession({
      sessionId: 'session-1', mediaStream, createClientSecret,
      sendAuditEvent: vi.fn().mockResolvedValue({ accepted: true }),
      fetchImpl: vi.fn().mockResolvedValue({ ok: true, text: async () => 'remote-sdp' }),
      RTCPeerConnectionImpl: FakePeerConnection,
    });
    await session.connect();

    const reconnecting = session.reconnect();
    await vi.advanceTimersByTimeAsync(0);
    session.cancelReconnect();

    await expect(reconnecting).resolves.toBe(false);
    await vi.runAllTimersAsync();
    expect(createClientSecret).toHaveBeenCalledTimes(2);
    expect(session.getState().status).toBe('disconnected');
  });

  it('does not reconnect after the user ends while waiting for throttle', async () => {
    vi.useFakeTimers();
    const throttle = Object.assign(new Error('too recent'), {
      response: { status: 409, headers: { 'retry-after': '30' } },
    });
    const createClientSecret = vi.fn()
      .mockResolvedValueOnce({ client_secret: 'ek_initial' })
      .mockRejectedValueOnce(throttle);
    const session = createRealtimeSession({
      sessionId: 'session-1', mediaStream, createClientSecret,
      sendAuditEvent: vi.fn().mockResolvedValue({ accepted: true }),
      fetchImpl: vi.fn().mockResolvedValue({ ok: true, text: async () => 'remote-sdp' }),
      RTCPeerConnectionImpl: FakePeerConnection,
    });
    await session.connect();

    const reconnecting = session.reconnect();
    await vi.advanceTimersByTimeAsync(0);
    await session.disconnect('user_ended');

    await expect(reconnecting).resolves.toBe(false);
    await vi.runAllTimersAsync();
    expect(createClientSecret).toHaveBeenCalledTimes(2);
    await expect(session.reconnect()).resolves.toBe(false);
  });

  it('fails closed when microphone permission is revoked before reconnect', async () => {
    const createClientSecret = vi.fn().mockResolvedValue({ client_secret: 'ek_initial' });
    const errorListener = vi.fn();
    const session = createRealtimeSession({
      sessionId: 'session-1', mediaStream, createClientSecret,
      sendAuditEvent: vi.fn().mockResolvedValue({ accepted: true }),
      fetchImpl: vi.fn().mockResolvedValue({ ok: true, text: async () => 'remote-sdp' }),
      RTCPeerConnectionImpl: FakePeerConnection,
    });
    session.on('error', errorListener);
    await session.connect();
    track.readyState = 'ended';

    await expect(session.reconnect()).rejects.toThrow('Microphone permission');
    expect(createClientSecret).toHaveBeenCalledTimes(1);
    expect(errorListener).toHaveBeenCalledWith(expect.objectContaining({
      code: 'MICROPHONE_UNAVAILABLE', retryable: false,
    }));
  });

  it('backs off while offline and reconnects once the network returns', async () => {
    vi.useFakeTimers();
    let online = true;
    const createClientSecret = vi.fn().mockResolvedValue({ client_secret: 'ek_memory_only' });
    const session = createRealtimeSession({
      sessionId: 'session-1', mediaStream, createClientSecret,
      sendAuditEvent: vi.fn().mockResolvedValue({ accepted: true }),
      fetchImpl: vi.fn().mockResolvedValue({ ok: true, text: async () => 'remote-sdp' }),
      RTCPeerConnectionImpl: FakePeerConnection,
      isOnline: () => online,
    });
    await session.connect();
    online = false;

    const reconnecting = session.reconnect();
    await Promise.resolve();
    await Promise.resolve();
    expect(createClientSecret).toHaveBeenCalledTimes(1);
    online = true;
    await vi.advanceTimersByTimeAsync(1_000);
    await expect(reconnecting).resolves.toBe(true);
    expect(createClientSecret).toHaveBeenCalledTimes(2);
  });

  it('reports an unexpected data-channel close and deduplicates replayed transcripts', async () => {
    const sendAuditEvent = vi.fn().mockResolvedValue({ accepted: true });
    const errorListener = vi.fn();
    const transcriptListener = vi.fn();
    const session = createRealtimeSession({
      sessionId: 'session-1', mediaStream,
      createClientSecret: vi.fn().mockResolvedValue({ client_secret: 'ek_memory_only' }),
      sendAuditEvent,
      fetchImpl: vi.fn().mockResolvedValue({ ok: true, text: async () => 'remote-sdp' }),
      RTCPeerConnectionImpl: FakePeerConnection,
    });
    session.on('error', errorListener).on('transcript', transcriptListener);
    await session.connect();
    const channel = FakePeerConnection.instances[0].channel;
    channel.dispatchEvent(new Event('open'));
    const event = {
      type: 'response.output_audio_transcript.done',
      item_id: 'ai-replayed',
      transcript: 'Hãy mô tả dự án gần nhất.',
    };
    channel.providerEvent(event);
    channel.providerEvent({ ...event, item_id: 'ai-replayed-new-id' });
    channel.dispatchEvent(new Event('close'));
    await Promise.resolve();

    expect(transcriptListener).toHaveBeenCalledTimes(1);
    expect(session.getState().turns).toHaveLength(1);
    expect(errorListener).toHaveBeenCalledWith(expect.objectContaining({
      code: 'WEBRTC_DATA_CHANNEL_CLOSED', retryable: true,
    }));
  });
});
