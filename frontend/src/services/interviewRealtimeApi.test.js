import { beforeEach, describe, expect, it, vi } from 'vitest';

const apiClient = vi.hoisted(() => ({ post: vi.fn(), get: vi.fn(), delete: vi.fn() }));
vi.mock('./apiClient', () => ({ default: apiClient }));

import {
  createRealtimeInterviewSession,
  deleteRealtimeInterviewSession,
} from './interviewRealtimeApi';

describe('realtime session API boundary', () => {
  beforeEach(() => apiClient.post.mockReset().mockResolvedValue({ data: { id: 'session-1' } }));

  it('pins Vietnamese and recording-off without forwarding provider overrides', async () => {
    await createRealtimeInterviewSession({
      application_id: 'app-1',
      consent_audio: true,
      language: 'en',
      instructions: 'Speak English',
      model: 'browser-model',
      client_secret: 'do-not-forward',
    });

    const payload = apiClient.post.mock.calls[0][1];
    expect(payload).toEqual(expect.objectContaining({
      application_id: 'app-1',
      consent_audio: true,
      consent_camera: false,
      consent_recording: false,
      language: 'vi',
    }));
    expect(payload).not.toHaveProperty('instructions');
    expect(payload).not.toHaveProperty('model');
    expect(payload).not.toHaveProperty('client_secret');
  });

  it('uses the owner-scoped privacy deletion endpoint without a request body', async () => {
    apiClient.delete.mockReset().mockResolvedValue({ status: 204 });

    await deleteRealtimeInterviewSession('session-1');

    expect(apiClient.delete).toHaveBeenCalledWith(
      '/v1/interview/realtime/sessions/session-1'
    );
  });
});
