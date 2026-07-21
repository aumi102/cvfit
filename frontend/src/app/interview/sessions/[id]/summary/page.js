'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import { getRealtimeInterviewSummary } from '@/services/interviewRealtimeApi';
import PageShell from '@/components/common/PageShell';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import styles from '@/styles/InterviewRoom.module.css';

const RUBRIC_LABELS = {
  relevance: 'Mức độ liên quan',
  specificity: 'Tính cụ thể',
  evidence: 'Bằng chứng',
  structure: 'Cấu trúc',
  technical_depth: 'Chiều sâu kỹ thuật',
  communication_clarity: 'Độ rõ ràng',
  risk: 'Rủi ro tuyên bố thiếu căn cứ',
};

export default function InterviewSummaryPage() {
  const { isAuthChecking } = useRequireAuth();
  const { id } = useParams();
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [retryToken, setRetryToken] = useState(0);

  const loadSummary = useCallback(async () => {
    setError(null);
    try {
      const data = await getRealtimeInterviewSummary(id);
      setSummary(data);
      return data.status;
    } catch {
      setError('Không thể tải đánh giá phỏng vấn.');
      return 'error';
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (isAuthChecking) return undefined;
    let active = true;
    let timer = null;

    const poll = async () => {
      const status = await loadSummary();
      if (active && status === 'pending') {
        timer = setTimeout(poll, 2000);
      }
    };
    void poll();

    return () => {
      active = false;
      if (timer) clearTimeout(timer);
    };
  }, [isAuthChecking, loadSummary, retryToken]);

  if (isAuthChecking || isLoading) {
    return (
      <PageShell isAuthChecking={isAuthChecking} maxWidth="960px">
        <LoadingSpinner fullPage label="Đang tạo đánh giá…" />
      </PageShell>
    );
  }

  if (error) {
    return (
      <PageShell isAuthChecking={false} maxWidth="960px">
        <div className={styles.summaryStateCard} role="alert">
          <h1>Tạo đánh giá thất bại</h1>
          <p>{error}</p>
          <button type="button" className={styles.btnPrimary} onClick={() => {
            setIsLoading(true);
            setRetryToken((value) => value + 1);
          }}>
            Thử lại
          </button>
        </div>
      </PageShell>
    );
  }

  if (!summary || summary.status === 'pending') {
    return (
      <PageShell isAuthChecking={false} maxWidth="960px">
        <div className={styles.summaryStateCard} aria-live="polite">
          <LoadingSpinner label="Đang tạo đánh giá…" />
          <p>Bản ghi đã được gửi an toàn. Vui lòng chờ trong giây lát.</p>
        </div>
      </PageShell>
    );
  }

  if (summary.status === 'failed') {
    return (
      <PageShell isAuthChecking={false} maxWidth="960px">
        <div className={styles.summaryStateCard} role="alert">
          <h1>Tạo đánh giá thất bại</h1>
          <p>Dữ liệu lượt lời vẫn được giữ lại an toàn để bạn thử tải lại đánh giá.</p>
          <button type="button" className={styles.btnPrimary} onClick={() => {
            setIsLoading(true);
            setRetryToken((value) => value + 1);
          }}>
            Thử tải lại
          </button>
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell isAuthChecking={false} maxWidth="960px">
      <div className={styles.summaryContainer}>
        <header className={styles.summaryHeader}>
          <span className={styles.voiceLanguageBadge}>Tiếng Việt</span>
          <h1 className={styles.summaryTitle}>Đánh giá buổi phỏng vấn</h1>
          <p className={styles.summarySubtitle}>{summary.disclaimer}</p>
        </header>

        <div className={styles.summaryScoreCard}>
          <strong>{summary.overall_score ?? '—'}</strong>
          <span>/100 điểm luyện tập</span>
        </div>

        <section className={styles.rubricCards} aria-label="Chi tiết rubric">
          {Object.entries(summary.rubric || {}).map(([key, item]) => (
            <div key={key} className={styles.rubricCard}>
              <div className={styles.rubricCardLabel}>{RUBRIC_LABELS[key] || key}</div>
              <div className={styles.rubricCardScore}>
                {item?.score ?? '—'} <span className={styles.rubricCardMax}>/ {item?.max_score ?? 5}</span>
              </div>
            </div>
          ))}
        </section>

        <div className={styles.summaryInsightGrid}>
          <SummaryList title="Điểm mạnh" items={summary.strengths} />
          <SummaryList title="Điểm cần cải thiện" items={summary.weaknesses} />
          <SummaryList title="Khuyến nghị" items={summary.suggested_improvements} />
          <SummaryList title="Câu hỏi luyện tập tiếp theo" items={summary.next_practice_questions} />
        </div>

        <section className={styles.summaryLimitations}>
          <h2>Giới hạn đánh giá</h2>
          <ul>{(summary.limitations || []).map((item) => <li key={item}>{item}</li>)}</ul>
        </section>

        <div className={styles.summaryActions}>
          <Link href="/interview/sessions/new" className={styles.btnPrimary}>Luyện tập tiếp</Link>
          <Link href="/interview/sessions" className={styles.btnSecondary}>Về danh sách phiên</Link>
        </div>
      </div>
    </PageShell>
  );
}

function SummaryList({ title, items = [] }) {
  return (
    <section className={styles.summaryInsightCard}>
      <h2>{title}</h2>
      {items.length > 0 ? (
        <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul>
      ) : (
        <p>Chưa có dữ liệu.</p>
      )}
    </section>
  );
}
