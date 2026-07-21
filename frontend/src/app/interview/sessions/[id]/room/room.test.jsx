import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import InterviewRoomPage from './page';

const mocks = vi.hoisted(() => ({
  media: {},
  interview: {},
  getSession: vi.fn(),
  complete: vi.fn(),
  replace: vi.fn(),
}));

vi.mock('next/navigation', () => ({
  useParams: () => ({ id: 'session-1' }),
  useRouter: () => ({ replace: mocks.replace }),
}));
vi.mock('@/hooks/useRequireAuth', () => ({ useRequireAuth: () => ({ isAuthChecking: false }) }));
vi.mock('@/hooks/useMediaDevices', () => ({ useMediaDevices: () => mocks.media }));
vi.mock('@/hooks/useInterviewSession', () => ({ useInterviewSession: () => mocks.interview }));
vi.mock('@/services/interviewRealtimeApi', () => ({
  getRealtimeInterviewSession: (...args) => mocks.getSession(...args),
  completeRealtimeInterviewSession: (...args) => mocks.complete(...args),
}));
vi.mock('@/components/common/PageShell', () => ({ default: ({ children }) => <main>{children}</main> }));

function baseMedia(overrides = {}) {
  return {
    micStatus: 'granted',
    micStream: { getAudioTracks: () => [{ enabled: true }] },
    audioLevel: 0,
    isMuted: false,
    toggleMute: vi.fn(),
    requestMic: vi.fn().mockResolvedValue({ granted: true }),
    stopAll: vi.fn(),
    ...overrides,
  };
}

function baseInterview(overrides = {}) {
  return {
    status: 'idle',
    isAISpeaking: false,
    isUserSpeaking: false,
    isProcessing: false,
    transcript: [],
    turns: [],
    error: null,
    elapsedTime: 0,
    connect: vi.fn().mockResolvedValue(undefined),
    disconnect: vi.fn().mockResolvedValue(undefined),
    reconnect: vi.fn().mockResolvedValue(undefined),
    ...overrides,
  };
}

describe('realtime voice room UX', () => {
  beforeEach(() => {
    mocks.media = baseMedia();
    mocks.interview = baseInterview();
    mocks.getSession.mockReset().mockResolvedValue({
      id: 'session-1',
      application_id: 'app-1',
      question_limit: 5,
      language: 'vi',
    });
    mocks.complete.mockReset().mockResolvedValue({ summary_status: 'ready' });
    mocks.replace.mockReset();
  });

  it('shows a readable permission-denied state with retry and text fallback', async () => {
    mocks.media = baseMedia({
      micStatus: 'denied',
      micStream: null,
      requestMic: vi.fn().mockResolvedValue({ granted: false, error: 'Quyền microphone đã bị từ chối.' }),
    });
    render(<InterviewRoomPage />);

    fireEvent.click(await screen.findByRole('button', { name: /Bắt đầu phỏng vấn bằng giọng nói/i }));

    expect(await screen.findByRole('heading', { name: 'Không thể truy cập thiết bị' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Thử lại' })).toBeEnabled();
    expect(screen.getByRole('link', { name: 'Chuyển sang phỏng vấn bằng văn bản' }))
      .toHaveAttribute('href', '/applications/app-1/interview');
  });

  it('renders Vietnamese transcript, mute and idempotent completion controls', async () => {
    mocks.interview = baseInterview({
      status: 'connected',
      transcript: [
        { id: 'ai-1', speaker: 'ai', text: 'Hãy giới thiệu về dự án gần nhất.', timestamp: Date.now() },
        { id: 'user-1', speaker: 'user', text: 'Tôi đã xây dựng một API.', timestamp: Date.now() },
      ],
      turns: [{
        turn_index: 0,
        question_text: 'Hãy giới thiệu về dự án gần nhất.',
        answer_transcript: 'Tôi đã xây dựng một API.',
      }],
    });
    render(<InterviewRoomPage />);

    expect(await screen.findByText('Nhà tuyển dụng AI')).toBeInTheDocument();
    expect(screen.getByText('Tôi đã xây dựng một API.')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Tắt microphone' }));
    expect(mocks.media.toggleMute).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole('button', { name: 'Kết thúc phiên' }));
    await waitFor(() => expect(mocks.complete).toHaveBeenCalledWith(
      'session-1',
      expect.objectContaining({ completion_reason: 'user_ended' })
    ));
    expect(mocks.interview.disconnect).toHaveBeenCalledWith('user_ended');
    expect(mocks.media.stopAll).toHaveBeenCalled();
    expect(mocks.replace).toHaveBeenCalledWith('/interview/sessions/session-1/summary');
  });

  it('shows an explicit disabled/provider configuration message', async () => {
    mocks.getSession.mockRejectedValue({ response: { status: 503 } });
    render(<InterviewRoomPage />);

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Phỏng vấn bằng giọng nói hiện chưa được cấu hình.'
    );
    expect(screen.getByRole('button', { name: /Bắt đầu phỏng vấn bằng giọng nói/i })).toBeDisabled();
  });
});
