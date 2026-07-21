import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import HistoryPage from './page';

const getJobHistory = vi.hoisted(() => vi.fn());

vi.mock('next/link', () => ({
  default: ({ href, children, ...props }) => <a href={href} {...props}>{children}</a>,
}));
vi.mock('@/components/dashboard/Header', () => ({ default: () => <header>Header</header> }));
vi.mock('@/hooks/useRequireAuth', () => ({ useRequireAuth: () => ({ isAuthChecking: false }) }));
vi.mock('@/services/jobApi', () => ({ getJobHistory: (...args) => getJobHistory(...args) }));

describe('analysis history routing', () => {
  beforeEach(() => getJobHistory.mockReset());

  it('links a completed analysis to its stable detail route', async () => {
    getJobHistory.mockResolvedValue({
      items: [{
        job_id: 'job-123',
        status: 'succeeded',
        progress: 100,
        overall_fit_score: 82,
        target_role: 'Backend Developer',
        created_at: '2026-07-20T08:00:00Z',
      }],
    });
    render(<HistoryPage />);

    const link = await screen.findByRole('link', { name: 'Xem kết quả' });

    expect(link).toHaveAttribute('href', '/history/job-123');
    expect(link).not.toHaveAttribute('href', expect.stringContaining('/dashboard'));
  });

  it('clears loading and exposes a working retry after an API failure', async () => {
    getJobHistory
      .mockRejectedValueOnce(new Error('offline'))
      .mockResolvedValueOnce({ items: [] });
    render(<HistoryPage />);

    const retry = await screen.findByRole('button', { name: 'Thử lại' });
    fireEvent.click(retry);

    await waitFor(() => expect(getJobHistory).toHaveBeenCalledTimes(2));
    expect(await screen.findByText('Chưa có phân tích nào.')).toBeInTheDocument();
    expect(screen.queryByText('Đang tải lịch sử...')).not.toBeInTheDocument();
  });
});
