import { beforeEach, describe, expect, it, vi } from 'vitest';
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

const track = { enabled: true };
const mediaStream = { getAudioTracks: () => [track] };

describe('OpenAI Realtime WebRTC controller', () => {
  beforeEach(() => {
    FakePeerConnection.instances = [];
    localStorage.clear();
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
});
