import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import AnalysisDetailPage from './page';

const detailMocks = vi.hoisted(() => ({
  getJobResult: vi.fn(),
  getStoredAccessToken: vi.fn(),
  router: { push: vi.fn() },
}));
const { getJobResult, getStoredAccessToken, router } = detailMocks;

vi.mock('next/link', () => ({
  default: ({ href, children, ...props }) => <a href={href} {...props}>{children}</a>,
}));
vi.mock('next/navigation', () => ({
  useParams: () => ({ jobId: 'job-123' }),
  useRouter: () => detailMocks.router,
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock('@/hooks/useRequireAuth', () => ({ useRequireAuth: () => ({ isAuthChecking: false }) }));
vi.mock('@/components/dashboard/Header', () => ({ default: () => <header>Header</header> }));
vi.mock('@/components/dashboard/ResultCard', () => ({
  default: ({ onNewAnalysis }) => <button onClick={onNewAnalysis}>Action kết quả</button>,
}));
vi.mock('@/components/dashboard/ResultCardV2', () => ({
  default: ({ onNewAnalysis }) => <button onClick={onNewAnalysis}>Action kết quả V2</button>,
}));
vi.mock('@/components/results/ComparisonDashboard', () => ({ default: () => <div>So sánh</div> }));
vi.mock('@/components/common/LoadingSpinner', () => ({ default: ({ label }) => <div>{label}</div> }));
vi.mock('@/services/jobApi', () => ({
  getJobResult: (...args) => detailMocks.getJobResult(...args),
  getStoredAccessToken: (...args) => detailMocks.getStoredAccessToken(...args),
}));
vi.mock('@/utils/resultHelpers', () => ({ isResultV2: () => false }));

describe('analysis detail recovery', () => {
  beforeEach(() => {
    getJobResult.mockReset();
    getStoredAccessToken.mockReset().mockReturnValue(null);
    router.push.mockReset();
  });

  it('loads the authenticated historical result without an upload token and keeps actions clickable', async () => {
    getJobResult.mockResolvedValue({ overall_score: 82, matched_skills: [] });
    render(<AnalysisDetailPage />);

    const action = await screen.findByRole('button', { name: 'Action kết quả' });
    expect(screen.getByRole('heading', { name: 'Kết quả phân tích CV' })).toBeInTheDocument();
    expect(getJobResult).toHaveBeenCalledWith('job-123', null, expect.objectContaining({
      signal: expect.any(AbortSignal),
    }));

    fireEvent.click(action);
    expect(router.push).toHaveBeenCalledWith('/dashboard');
    expect(screen.queryByText('Đang tải kết quả phân tích…')).not.toBeInTheDocument();
  });

  it('shows a 404 state and retries without redirecting to upload', async () => {
    getJobResult
      .mockRejectedValueOnce({ response: { status: 404 } })
      .mockResolvedValueOnce({ overall_score: 75 });
    render(<AnalysisDetailPage />);

    const retry = await screen.findByRole('button', { name: 'Thử lại' });
    expect(screen.getByText('Không tìm thấy kết quả phân tích.')).toBeInTheDocument();
    fireEvent.click(retry);

    await waitFor(() => expect(getJobResult).toHaveBeenCalledTimes(2));
    expect(await screen.findByRole('button', { name: 'Action kết quả' })).toBeEnabled();
    expect(router.push).not.toHaveBeenCalled();
  });
});
