'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import PageShell from '@/components/common/PageShell';
import ErrorBanner from '@/components/common/ErrorBanner';
import { createSession } from '@/services/interviewSessionsApi';
import { extractApiError } from '@/utils/errorHelpers';
import { trackEvent, ANALYTICS_EVENTS } from '@/lib/analytics';
import styles from '@/styles/InterviewSessions.module.css';

const QUESTION_TYPES = [
  { value: 'technical', label: 'Kỹ thuật', icon: '💻', desc: 'Code, hệ thống, giải quyết vấn đề' },
  { value: 'behavioral', label: 'Hành vi', icon: '🤝', desc: 'Làm việc nhóm, lãnh đạo, kể chuyện STAR' },
  { value: 'project', label: 'Dự án', icon: '📁', desc: 'Công việc cũ, thành tựu, mức độ ảnh hưởng' },
  { value: 'HR', label: 'Nhân sự / Văn hóa', icon: '🌐', desc: 'Phù hợp văn hóa, lương, mục tiêu nghề nghiệp' },
  { value: 'gap_check', label: 'Kiểm tra lỗ hổng', icon: '🔍', desc: 'Lỗ hổng kỹ năng từ phân tích CV' },
];

const DIFFICULTIES = [
  { value: 'easy', label: 'Dễ', icon: '🟢', desc: 'Khởi động, cơ bản' },
  { value: 'medium', label: 'Trung bình', icon: '🟡', desc: 'Mức phỏng vấn tiêu chuẩn' },
  { value: 'hard', label: 'Khó', icon: '🔴', desc: 'Cao cấp / cạnh tranh' },
];

export default function NewSessionPage() {
  const { isAuthChecking } = useRequireAuth();
  const router = useRouter();

  const [questionType, setQuestionType] = useState('behavioral');
  const [difficulty, setDifficulty] = useState('medium');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  async function handleStart(e) {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const session = await createSession({ question_type: questionType, difficulty });
      trackEvent(ANALYTICS_EVENTS.INTERVIEW_SESSION_CREATED, {
        feature_name: 'interview_sessions',
        question_type: questionType,
        difficulty,
      });
      router.push(`/interview/sessions/${session.id}`);
    } catch (err) {
      const { message } = extractApiError(err, 'Không thể bắt đầu phiên. Vui lòng thử lại.');
      setError(message);
      setIsSubmitting(false);
    }
  }

  return (
    <PageShell isAuthChecking={isAuthChecking} maxWidth="700px">
      {/* Breadcrumb */}
      <nav className={styles.breadcrumb} aria-label="Breadcrumb">
        <Link href="/interview/sessions">Luyện phỏng vấn</Link>
        <span className={styles.breadcrumbSep}>›</span>
        <span>Phiên mới</span>
      </nav>

      <div className={styles.formCard}>
        <h1 className={styles.formTitle}>Bắt đầu phiên luyện tập</h1>
        <p className={styles.formSubtitle}>
          Chọn loại câu hỏi và độ khó. AI sẽ tạo các câu hỏi nhắm mục tiêu và cung cấp phản hồi theo tiêu chí cho câu trả lời của bạn.
        </p>

        {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

        <form onSubmit={handleStart} id="new-session-form">
          {/* Question Type */}
          <div className={styles.fieldGroup}>
            <label className={styles.fieldLabel}>Loại câu hỏi</label>
            <div className={styles.optionGrid}>
              {QUESTION_TYPES.map((qt) => (
                <button
                  key={qt.value}
                  type="button"
                  className={`${styles.optionCard} ${questionType === qt.value ? styles['optionCard--selected'] : ''}`}
                  onClick={() => setQuestionType(qt.value)}
                  id={`qtype-${qt.value}`}
                >
                  <div className={styles.optionIcon}>{qt.icon}</div>
                  <div className={styles.optionLabel}>{qt.label}</div>
                  <div className={styles.optionDesc}>{qt.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Difficulty */}
          <div className={styles.fieldGroup}>
            <label className={styles.fieldLabel}>Độ khó</label>
            <div className={styles.optionGrid} style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
              {DIFFICULTIES.map((d) => (
                <button
                  key={d.value}
                  type="button"
                  className={`${styles.optionCard} ${difficulty === d.value ? styles['optionCard--selected'] : ''}`}
                  onClick={() => setDifficulty(d.value)}
                  id={`difficulty-${d.value}`}
                >
                  <div className={styles.optionIcon}>{d.icon}</div>
                  <div className={styles.optionLabel}>{d.label}</div>
                  <div className={styles.optionDesc}>{d.desc}</div>
                </button>
              ))}
            </div>
          </div>

          <div className={styles.formActions}>
            <Link href="/interview/sessions" className={styles.btnSecondary}>
              Hủy
            </Link>
            <button
              type="submit"
              className={styles.btnPrimary}
              disabled={isSubmitting}
              id="start-session-btn"
            >
              {isSubmitting ? (
                <>
                  <span style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%', animation: 'spin 0.7s linear infinite', display: 'inline-block' }} />
                  Đang bắt đầu…
                </>
              ) : (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="5 3 19 12 5 21 5 3" />
                  </svg>
                  Bắt đầu phiên
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </PageShell>
  );
}
