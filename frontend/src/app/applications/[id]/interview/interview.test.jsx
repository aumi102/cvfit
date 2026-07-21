import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import InterviewPage from './page';

const interviewMocks = vi.hoisted(() => ({
  getInterviewQuestions: vi.fn(),
  getAnswers: vi.fn(),
  submitAnswer: vi.fn(),
}));
const { getInterviewQuestions, getAnswers, submitAnswer } = interviewMocks;

vi.mock('next/navigation', () => ({ useParams: () => ({ id: 'app-1' }) }));
vi.mock('next/link', () => ({
  default: ({ href, children, ...props }) => <a href={href} {...props}>{children}</a>,
}));
vi.mock('@/hooks/useRequireAuth', () => ({ useRequireAuth: () => ({ isAuthChecking: false }) }));
vi.mock('@/components/common/PageShell', () => ({ default: ({ children }) => <main>{children}</main> }));
vi.mock('@/components/common/LoadingSpinner', () => ({ default: ({ label }) => <div>{label}</div> }));
vi.mock('@/components/common/ErrorBanner', () => ({ default: ({ message }) => <div role="alert">{message}</div> }));
vi.mock('@/components/common/EmptyStatePage', () => ({ default: ({ title }) => <div>{title}</div> }));
vi.mock('@/components/common/RiskBadge', () => ({ default: () => <span>risk</span> }));
vi.mock('@/components/common/Disclaimer', () => ({ default: ({ text }) => <p>{text}</p> }));
vi.mock('@/lib/analytics', () => ({
  trackEvent: vi.fn(),
  ANALYTICS_EVENTS: { INTERVIEW_START: 'start', INTERVIEW_ANSWER_SUBMITTED: 'answer' },
}));
vi.mock('@/services/interviewApi', () => ({
  getInterviewQuestions: (...args) => interviewMocks.getInterviewQuestions(...args),
  getAnswers: (...args) => interviewMocks.getAnswers(...args),
  submitAnswer: (...args) => interviewMocks.submitAnswer(...args),
}));

describe('Vietnamese interview modes', () => {
  beforeEach(() => {
    getInterviewQuestions.mockResolvedValue({
      questions: [{ question_id: 'q-1', question: 'Hãy mô tả một dự án thử thách.', type: 'behavioral' }],
      disclaimer: 'Nội dung luyện tập.',
    });
    getAnswers.mockResolvedValue({ answers: [] });
    submitAnswer.mockResolvedValue({
      rubric: { overall: 4 },
      feedback: { strengths: ['Trả lời rõ ràng.'], disclaimer: 'Hãy xem lại.' },
    });
  });

  it('shows voice as a visible first-class mode and keeps text practice usable', async () => {
    render(<InterviewPage />);

    expect(screen.getByRole('tab', { name: 'Phỏng vấn bằng giọng nói' })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('link', { name: 'Bắt đầu phỏng vấn bằng giọng nói' }))
      .toHaveAttribute('href', '/interview/sessions/new?application_id=app-1');
    expect(screen.getByText(/không ghi âm/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: 'Luyện tập bằng văn bản' }));
    expect(await screen.findByText('Hãy mô tả một dự án thử thách.')).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Câu trả lời cho câu hỏi 1'), {
      target: { value: 'Tôi đã xây dựng một API và đo lường kết quả.' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Nộp câu trả lời' }));

    expect(await screen.findByText('Trả lời rõ ràng.')).toBeInTheDocument();
    expect(submitAnswer).toHaveBeenCalledWith('app-1', expect.objectContaining({
      answer_text: 'Tôi đã xây dựng một API và đo lường kết quả.',
    }));
  });
});
