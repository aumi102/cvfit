'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import { getSessionSummary } from '@/services/interviewSessionsApi';
import { MOCK_SUMMARY, RUBRIC_KEYS, RUBRIC_LABELS, RUBRIC_DESCS } from '@/lib/interviewTypes';
import PageShell from '@/components/common/PageShell';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ErrorBanner from '@/components/common/ErrorBanner';
import styles from '@/styles/InterviewRoom.module.css';

export default function InterviewSummaryPage() {
  const { isAuthChecking } = useRequireAuth();
  const { id } = useParams();
  const router = useRouter();

  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedQaId, setExpandedQaId] = useState(null);

  useEffect(() => {
    if (isAuthChecking) return;
    let active = true;

    async function loadSummary() {
      try {
        const data = await getSessionSummary(id);
        if (!active) return;
        
        // If the backend isn't ready, use our mock data
        setSummary(data || MOCK_SUMMARY);
      } catch (err) {
        if (!active) return;
        console.error("Error loading summary:", err);
        // Fall back to mock on error to ensure UI is testable
        setSummary(MOCK_SUMMARY);
      } finally {
        if (active) setIsLoading(false);
      }
    }

    loadSummary();

    return () => { active = false; };
  }, [id, isAuthChecking]);

  const handleExport = () => {
    if (!summary) return;
    const lines = [];
    lines.push(`Kết quả phỏng vấn`);
    lines.push(`Điểm tổng quát: ${summary.overall_score}/10`);
    lines.push('');
    
    lines.push(`Điểm chi tiết:`);
    RUBRIC_KEYS.forEach(key => {
      if (summary.rubric[key] !== undefined) {
        lines.push(`- ${RUBRIC_LABELS[key]}: ${summary.rubric[key]}/10`);
      }
    });
    lines.push('');

    lines.push(`Điểm mạnh:`);
    summary.strengths?.forEach(s => lines.push(`- ${s}`));
    lines.push('');

    lines.push(`Điểm yếu cần khắc phục:`);
    summary.weaknesses?.forEach(w => lines.push(`- ${w}`));
    lines.push('');

    lines.push(`Gợi ý cải thiện:`);
    summary.improvements?.forEach(i => lines.push(`- ${i}`));
    lines.push('');

    const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `interview-summary-${id}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (isAuthChecking || isLoading) {
    return (
      <PageShell isAuthChecking={isAuthChecking} maxWidth="960px">
        <LoadingSpinner fullPage label="Đang tổng hợp kết quả..." />
      </PageShell>
    );
  }

  if (error || !summary) {
    return (
      <PageShell isAuthChecking={isAuthChecking} maxWidth="960px">
        <ErrorBanner message={error || "Không thể tải kết quả phỏng vấn."} />
      </PageShell>
    );
  }

  // Calculate SVG circle dashoffset
  const circumference = 2 * Math.PI * 62; // r=62
  const pct = Math.max(0, Math.min(10, summary.overall_score || 0)) / 10;
  const strokeDashoffset = circumference - pct * circumference;

  return (
    <PageShell isAuthChecking={isAuthChecking} maxWidth="960px">
      <div className={styles.summaryContainer}>
        
        {/* Header */}
        <div className={styles.summaryHeader}>
          <div style={{ display: 'inline-flex', padding: '4px 12px', background: 'var(--color-primary-light)', color: 'var(--color-primary)', borderRadius: 'var(--radius-full)', fontSize: 'var(--font-size-xs)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '1rem' }}>
            Phân tích hoàn tất
          </div>
          <h1 className={styles.summaryTitle}>Kết quả phỏng vấn</h1>
          <p className={styles.summarySubtitle}>
            AI đã phân tích phần trả lời của bạn. Xem đánh giá chi tiết và lộ trình cải thiện bên dưới.
          </p>
        </div>

        {/* Score Circle */}
        <div className={styles.scoreCircleWrap}>
          <div className={styles.scoreCircle}>
            <svg viewBox="0 0 140 140">
              <defs>
                <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#7C3AED" />
                  <stop offset="100%" stopColor="#4F46E5" />
                </linearGradient>
              </defs>
              <circle className={styles.scoreCircleTrack} cx="70" cy="70" r="62" />
              <circle 
                className={styles.scoreCircleFill} 
                cx="70" cy="70" r="62" 
                strokeDasharray={circumference}
                style={{ '--circumference': circumference, strokeDashoffset, animation: 'drawCircle 1.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards' }}
              />
            </svg>
            <div className={styles.scoreCircleValue}>
              <div className={styles.scoreNumber}>{summary.overall_score}</div>
              <div className={styles.scoreMax}>/10</div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginBottom: '3rem' }}>
          <button className={styles.btnSecondary} onClick={handleExport}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Xuất báo cáo
          </button>
          <Link href="/interview/sessions/new" className={styles.btnPrimary}>
            Luyện tập tiếp
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12" />
              <line x1="12" y1="5" x2="19" y2="12" />
              <line x1="12" y1="19" x2="19" y2="12" />
            </svg>
          </Link>
        </div>

        {/* Rubric Cards */}
        {summary.rubric && (
          <div className={styles.rubricCards}>
            {RUBRIC_KEYS.map(key => {
              const score = summary.rubric[key];
              if (score === undefined) return null;
              const fillPct = (score / 10) * 100;
              return (
                <div key={key} className={styles.rubricCard} title={RUBRIC_DESCS[key]}>
                  <div className={styles.rubricCardLabel}>{RUBRIC_LABELS[key]}</div>
                  <div className={styles.rubricCardScore}>
                    {score}
                    <span className={styles.rubricCardMax}>/10</span>
                  </div>
                  <div className={styles.rubricCardBar}>
                    <div className={styles.rubricCardBarFill} style={{ width: `${fillPct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Insights (Strengths / Weaknesses) */}
        <div className={styles.insightsGrid}>
          {summary.strengths?.length > 0 && (
            <div className={`${styles.insightCard} ${styles['insightCard--strength']}`}>
              <div className={`${styles.insightTitle} ${styles['insightTitle--strength']}`}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
                Điểm mạnh
              </div>
              <div className={styles.insightList}>
                {summary.strengths.map((s, i) => (
                  <div key={i} className={styles.insightItem}>
                    <div className={`${styles.insightBullet} ${styles['insightBullet--strength']}`} />
                    {s}
                  </div>
                ))}
              </div>
            </div>
          )}

          {summary.weaknesses?.length > 0 && (
            <div className={`${styles.insightCard} ${styles['insightCard--weakness']}`}>
              <div className={`${styles.insightTitle} ${styles['insightTitle--weakness']}`}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                Điểm cần khắc phục
              </div>
              <div className={styles.insightList}>
                {summary.weaknesses.map((w, i) => (
                  <div key={i} className={styles.insightItem}>
                    <div className={`${styles.insightBullet} ${styles['insightBullet--weakness']}`} />
                    {w}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Q&A Accordion */}
        {summary.questions?.length > 0 && (
          <div className={styles.qaSection}>
            <h2 className={styles.qaSectionTitle}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
              Chi tiết câu trả lời
            </h2>
            <div className={styles.qaList}>
              {summary.questions.map((q, i) => {
                const isOpen = expandedQaId === q.id;
                return (
                  <div key={q.id} className={styles.qaItem}>
                    <button 
                      className={styles.qaItemHeader} 
                      onClick={() => setExpandedQaId(isOpen ? null : q.id)}
                    >
                      <div className={styles.qaItemNum}>{i + 1}</div>
                      <div className={styles.qaItemQuestion}>{q.text}</div>
                      <div className={styles.qaItemScore}>{q.score}<span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', fontWeight: 500 }}>/10</span></div>
                      <svg className={`${styles.qaItemChevron} ${isOpen ? styles['qaItemChevron--open'] : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="6 9 12 15 18 9" />
                      </svg>
                    </button>
                    {isOpen && (
                      <div className={styles.qaItemBody}>
                        <div className={styles.qaAnswerLabel}>Câu trả lời của bạn</div>
                        <p className={styles.qaAnswerText}>&quot;{q.answer}&quot;</p>
                        
                        <div className={styles.qaAnswerLabel}>Nhận xét từ AI</div>
                        <p className={styles.qaFeedbackText}>{q.feedback}</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Improvements */}
        {summary.improvements?.length > 0 && (
          <div className={styles.improvementsCard}>
            <h2 className={styles.qaSectionTitle} style={{ marginBottom: '1.5rem', color: '#5B21B6' }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
                <polyline points="17 6 23 6 23 12" />
              </svg>
              Hướng cải thiện
            </h2>
            <div>
              {summary.improvements.map((imp, i) => (
                <div key={i} className={styles.improvementItem}>
                  <div className={styles.improvementNum}>{i + 1}</div>
                  <div style={{ marginTop: 2 }}>{imp}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Next Practice Questions */}
        {summary.next_questions?.length > 0 && (
          <div className={styles.nextQuestionsCard}>
            <h2 className={styles.qaSectionTitle} style={{ marginBottom: '1.5rem' }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
              Câu hỏi luyện tập tiếp theo
            </h2>
            <div>
              {summary.next_questions.map((q, i) => (
                <div key={i} className={styles.nextQuestionItem}>
                  <div className={styles.nextQuestionBullet}>✓</div>
                  {q}
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </PageShell>
  );
}
