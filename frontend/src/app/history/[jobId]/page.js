'use client';

import { Suspense, useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import Header from '@/components/dashboard/Header';
import ResultCard from '@/components/dashboard/ResultCard';
import ResultCardV2 from '@/components/dashboard/ResultCardV2';
import ComparisonDashboard from '@/components/results/ComparisonDashboard';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import { getJobResult, getStoredAccessToken } from '@/services/jobApi';
import { isResultV2 } from '@/utils/resultHelpers';
import styles from '@/styles/History.module.css';

function errorMessage(error) {
  if (error?.response?.status === 404) return 'Không tìm thấy kết quả phân tích.';
  if (error?.response?.status === 403) return 'Bạn không có quyền xem kết quả phân tích này.';
  return 'Không thể tải kết quả phân tích. Vui lòng thử lại.';
}

function AnalysisDetailContent() {
  const { isAuthChecking } = useRequireAuth();
  const { jobId } = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const compareWith = searchParams.get('compare_with');
  const [result, setResult] = useState(null);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reloadKey, setReloadKey] = useState(0);

  const load = useCallback(async (signal) => {
    setIsLoading(true);
    setError(null);
    try {
      const currentToken = getStoredAccessToken(jobId);
      const requests = [getJobResult(jobId, currentToken, { signal })];
      if (compareWith) {
        requests.push(getJobResult(compareWith, getStoredAccessToken(compareWith), { signal }));
      }
      const [current, previous] = await Promise.all(requests);
      setResult(current);
      setComparisonResult(previous || null);
    } catch (cause) {
      if (cause?.code === 'ERR_CANCELED') return;
      setError(errorMessage(cause));
    } finally {
      if (!signal.aborted) setIsLoading(false);
    }
  }, [compareWith, jobId]);

  useEffect(() => {
    if (isAuthChecking) return undefined;
    const controller = new AbortController();
    void load(controller.signal);
    return () => controller.abort();
  }, [isAuthChecking, load, reloadKey]);

  return (
    <div className={styles.page}>
      <Header />
      <main className={styles.detailMain}>
        <nav className={styles.detailBreadcrumb} aria-label="Điều hướng lịch sử">
          <Link href="/history">← Lịch sử phân tích</Link>
        </nav>

        {isAuthChecking || isLoading ? (
          <div className={styles.detailState} aria-live="polite">
            <LoadingSpinner label="Đang tải kết quả phân tích…" />
          </div>
        ) : error ? (
          <div className={styles.detailState} role="alert">
            <h1>{error}</h1>
            <p>Dữ liệu lịch sử không bị thay đổi.</p>
            <button type="button" onClick={() => setReloadKey((value) => value + 1)}>
              Thử lại
            </button>
            <Link href="/history">Quay lại lịch sử</Link>
          </div>
        ) : (
          <div className={styles.detailContent}>
            <div className={styles.detailHeader}>
              <div>
                <h1>Kết quả phân tích CV</h1>
                <p>Mã phân tích: {jobId}</p>
              </div>
              <Link href="/dashboard" className={styles.dashboardLink}>Phân tích CV mới</Link>
            </div>

            {comparisonResult && (
              <ComparisonDashboard previousResult={comparisonResult} currentResult={result} />
            )}

            {isResultV2(result) ? (
              <ResultCardV2
                result={result}
                jobId={jobId}
                accessToken={getStoredAccessToken(jobId)}
                onNewAnalysis={() => router.push('/dashboard')}
              />
            ) : (
              <ResultCard
                result={result}
                jobId={jobId}
                accessToken={getStoredAccessToken(jobId)}
                onNewAnalysis={() => router.push('/dashboard')}
              />
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default function AnalysisDetailPage() {
  return (
    <Suspense fallback={<div className={styles.detailState}>Đang tải…</div>}>
      <AnalysisDetailContent />
    </Suspense>
  );
}
