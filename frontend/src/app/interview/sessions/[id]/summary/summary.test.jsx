import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import InterviewSummaryPage from './page';

const mocks = vi.hoisted(() => ({
  getSummary: vi.fn(),
  deleteSession: vi.fn(),
  replace: vi.fn(),
}));

vi.mock('next/navigation', () => ({
  useParams: () => ({ id: 'session-1' }),
  useRouter: () => ({ replace: mocks.replace }),
}));
vi.mock('next/link', () => ({
  default: ({ href, children, ...props }) => <a href={href} {...props}>{children}</a>,
}));
vi.mock('@/hooks/useRequireAuth', () => ({ useRequireAuth: () => ({ isAuthChecking: false }) }));
vi.mock('@/services/interviewRealtimeApi', () => ({
  getRealtimeInterviewSummary: (...args) => mocks.getSummary(...args),
  deleteRealtimeInterviewSession: (...args) => mocks.deleteSession(...args),
}));
vi.mock('@/components/common/PageShell', () => ({ default: ({ children }) => <main>{children}</main> }));
vi.mock('@/components/common/LoadingSpinner', () => ({ default: ({ label }) => <div>{label}</div> }));

describe('realtime summary states', () => {
  beforeEach(() => {
    mocks.getSummary.mockReset();
    mocks.deleteSession.mockReset().mockResolvedValue(undefined);
    mocks.replace.mockReset();
  });

  it('renders a ready Vietnamese summary', async () => {
    mocks.getSummary.mockResolvedValue({
      status: 'ready',
      language: 'vi',
      overall_score: 78,
      rubric: { relevance: { score: 4, max_score: 5 } },
      strengths: ['Có bằng chứng cụ thể.'],
      weaknesses: ['Cần trả lời ngắn gọn hơn.'],
      suggested_improvements: ['Dùng cấu trúc STAR.'],
      next_practice_questions: ['Hãy mô tả một quyết định kỹ thuật.'],
      limitations: ['Đây là đánh giá luyện tập.'],
      disclaimer: 'Không dự đoán kết quả tuyển dụng.',
    });
    render(<InterviewSummaryPage />);

    expect(await screen.findByRole('heading', { name: 'Đánh giá buổi phỏng vấn' })).toBeInTheDocument();
    expect(screen.getByText('Có bằng chứng cụ thể.')).toBeInTheDocument();
    expect(screen.getByText('Không dự đoán kết quả tuyển dụng.')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Xóa dữ liệu phiên' }));
    expect(screen.getByText(/xóa vĩnh viễn transcript/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Xác nhận xóa' }));
    await waitFor(() => expect(mocks.deleteSession).toHaveBeenCalledWith('session-1'));
    expect(mocks.replace).toHaveBeenCalledWith('/interview/sessions');
  });

  it('surfaces a failed summary and allows a retry to ready', async () => {
    mocks.getSummary
      .mockResolvedValueOnce({ status: 'failed' })
      .mockResolvedValueOnce({
        status: 'ready', language: 'vi', overall_score: 70, rubric: {},
        strengths: [], weaknesses: [], suggested_improvements: [],
        next_practice_questions: [], limitations: [], disclaimer: 'Luyện tập.',
      });
    render(<InterviewSummaryPage />);

    const retry = await screen.findByRole('button', { name: 'Thử tải lại' });
    fireEvent.click(retry);

    await waitFor(() => expect(mocks.getSummary).toHaveBeenCalledTimes(2));
    expect(await screen.findByRole('heading', { name: 'Đánh giá buổi phỏng vấn' })).toBeInTheDocument();
  });
});
