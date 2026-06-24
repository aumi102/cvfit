'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import PageShell from '@/components/common/PageShell';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ErrorBanner from '@/components/common/ErrorBanner';
import EmptyStatePage from '@/components/common/EmptyStatePage';
import RiskBadge from '@/components/common/RiskBadge';
import Disclaimer from '@/components/common/Disclaimer';
import { getInterviewQuestions, submitAnswer, getAnswers } from '@/services/interviewApi';
import { extractApiError } from '@/utils/errorHelpers';
import { trackEvent, ANALYTICS_EVENTS } from '@/lib/analytics';
import styles from '@/styles/Interview.module.css';

/* ─────────────────────────────────────────
   Rubric row component
───────────────────────────────────────── */
function RubricRow({ label, value }) {
  if (value == null) return null;
  const pct = Math.round((value / 5) * 100);
  return (
    <div className={styles.rubricRow}>
      <span className={styles.rubricLabel}>{label}</span>
      <div className={styles.rubricBarWrap}>
        <div className={styles.rubricBar} style={{ width: `${pct}%` }} />
      </div>
      <span className={styles.rubricScore}>{value}/5</span>
    </div>
  );
}

/* ─────────────────────────────────────────
   Feedback section helper
───────────────────────────────────────── */
function FeedbackSection({ title, items }) {
  if (!items || (Array.isArray(items) && items.length === 0)) return null;
  const list = Array.isArray(items) ? items : [items];
  return (
    <div className={styles.feedbackSection}>
      <p className={styles.feedbackSectionTitle}>{title}</p>
      {list.map((item, i) => (
        <div key={i} className={styles.suggestionItem}>
          <span className={styles.suggestionBullet}>▸</span>
          <span>{typeof item === 'string' ? item : JSON.stringify(item)}</span>
        </div>
      ))}
    </div>
  );
}

/* ─────────────────────────────────────────
   Single question card
───────────────────────────────────────── */
function QuestionItem({ question, index, appId, pastAnswer }) {
  const [answerText, setAnswerText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState(null);   // { rubric, feedback }
  const [error, setError] = useState(null);
  const [showHistory, setShowHistory] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!answerText.trim()) return;
    setIsSubmitting(true);
    setError(null);
    try {
      const data = await submitAnswer(appId, {
        question_id: question.id || question.question_id || String(index),
        question: question.text || question.question || '',
        answer_text: answerText.trim(),
      });
      setResult(data);
      trackEvent(ANALYTICS_EVENTS.INTERVIEW_ANSWER_SUBMIT_SUCCESS, { feature_name: 'interview' });
    } catch (err) {
      const { message } = extractApiError(err, 'Không thể nộp câu trả lời. Vui lòng thử lại.');
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const rubric = result?.rubric || {};
  const feedback = result?.feedback || {};
  const overall = rubric.overall ?? null;
  const riskGap = rubric.risk_gap ?? null;

  return (
    <article
      className={styles.questionCard}
      style={{ animationDelay: `${index * 0.08}s` }}
      id={`question-${index + 1}`}
    >
      {/* Question header */}
      <div className={styles.questionHeader}>
        <span className={styles.questionNumber}>{index + 1}</span>
        <p className={styles.questionText}>{question.text || question.question || '—'}</p>
        {question.category && (
          <span className={styles.questionCategory}>{question.category}</span>
        )}
      </div>

      {/* Past answer badge */}
      {pastAnswer && !result && (
        <button
          className={styles.historyToggle}
          onClick={() => setShowHistory((v) => !v)}
          id={`history-toggle-${index + 1}`}
        >
          {showHistory ? '▲ Ẩn câu trả lời trước' : '▼ Hiển thị câu trả lời trước'}
        </button>
      )}
      {showHistory && pastAnswer && (
        <div className={styles.historyPanel}>
          <p className={styles.historyLabel}>Câu trả lời trước của bạn</p>
          <p className={styles.historyText}>{pastAnswer.answer_text}</p>
        </div>
      )}

      {/* Answer form or feedback */}
      {!result ? (
        <form onSubmit={handleSubmit} className={styles.answerForm}>
          <textarea
            className={styles.answerTextarea}
            value={answerText}
            onChange={(e) => setAnswerText(e.target.value)}
            placeholder="Nhập câu trả lời của bạn vào đây…"
            disabled={isSubmitting}
            id={`answer-textarea-${index + 1}`}
            aria-label={`Answer for question ${index + 1}`}
          />
          {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}
          <div className={styles.answerFooter}>
            <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
              {answerText.length} ký tự
            </span>
            <button
              type="submit"
              className={styles.submitBtn}
              disabled={isSubmitting || !answerText.trim()}
              id={`submit-answer-btn-${index + 1}`}
            >
              {isSubmitting ? (
                <><span className={styles.submitSpinner} /> Đang nộp…</>
              ) : (
                <>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                    strokeLinecap="round" strokeLinejoin="round" width="16" height="16">
                    <line x1="22" y1="2" x2="11" y2="13" />
                    <polygon points="22 2 15 22 11 13 2 9 22 2" />
                  </svg>
                  Nộp câu trả lời
                </>
              )}
            </button>
          </div>
        </form>
      ) : (
        <div className={styles.feedbackPanel}>
          {/* ── Header ── */}
          <p className={styles.feedbackTitle}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
              strokeLinecap="round" strokeLinejoin="round" width="16" height="16">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            Phản hồi AI
          </p>

          {/* ── Overall score + risk_gap ── */}
          <div className={styles.feedbackScore}>
            {overall != null && (
              <>
                <span className={styles.scoreValue}>{overall}</span>
                <div>
                  <div className={styles.scoreMeta}>tổng điểm / 5</div>
                  {riskGap != null && <RiskBadge score={riskGap} showScore />}
                </div>
              </>
            )}
            {riskGap != null && overall == null && (
              <RiskBadge score={riskGap} showScore />
            )}
          </div>

          {/* ── Rubric breakdown ── */}
          {Object.keys(rubric).some((k) => k !== 'overall' && k !== 'risk_gap' && rubric[k] != null) && (
            <div className={styles.rubricGrid}>
              <p className={styles.feedbackSuggestionsTitle}>Chi tiết điểm đánh giá</p>
              <RubricRow label="Mức độ liên quan"    value={rubric.relevance} />
              <RubricRow label="Tính cụ thể"  value={rubric.specificity} />
              <RubricRow label="Bằng chứng"     value={rubric.evidence} />
              <RubricRow label="Cấu trúc"    value={rubric.structure} />
              <RubricRow label="Rủi ro / Lỗ hổng"   value={rubric.risk_gap} />
            </div>
          )}

          {/* ── Feedback sections ── */}
          <FeedbackSection title="💪 Điểm mạnh"            items={feedback.strengths} />
          <FeedbackSection title="📎 Bằng chứng còn thiếu"     items={feedback.missing_evidence} />
          <FeedbackSection title="🔧 Đề xuất cải thiện" items={feedback.suggested_improvements} />
          <FeedbackSection title="📋 Dàn ý tham khảo"       items={feedback.sample_outline} />
          <FeedbackSection title="⚠️ Ghi chú rủi ro"           items={feedback.risk_notes} />

          {/* ── Disclaimer — always visible ── */}
          {feedback.disclaimer && (
            <div className={styles.inlineFeedbackDisclaimer}>
              <Disclaimer text={feedback.disclaimer} title="Lưu ý từ AI" />
            </div>
          )}

          {/* ── Retry ── */}
          <button
            className={styles.retryBtn}
            onClick={() => { setResult(null); setAnswerText(''); }}
            id={`retry-answer-btn-${index + 1}`}
          >
            ↩ Thử lại
          </button>
        </div>
      )}
    </article>
  );
}

/* ─────────────────────────────────────────
   Page
───────────────────────────────────────── */
export default function InterviewPage() {
  const { isAuthChecking } = useRequireAuth();
  const { id } = useParams();

  const [questions, setQuestions]   = useState([]);
  const [answers, setAnswers]       = useState([]);   // answer history
  const [isLoading, setIsLoading]   = useState(true);
  const [error, setError]           = useState(null);
  const [disclaimer, setDisclaimer] = useState(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Load questions and history in parallel
      const [qData, aData] = await Promise.allSettled([
        getInterviewQuestions(id),
        getAnswers(id),
      ]);

      if (qData.status === 'fulfilled') {
        const loadedQuestions = Array.isArray(qData.value?.questions) ? qData.value.questions : [];
        setQuestions(loadedQuestions);
        setDisclaimer(qData.value?.disclaimer || null);
        if (loadedQuestions.length > 0) {
          trackEvent(ANALYTICS_EVENTS.INTERVIEW_START, { feature_name: 'interview' });
        }
      } else {
        const { message } = extractApiError(qData.reason, 'Không thể tải câu hỏi phỏng vấn.');
        setError(message);
      }

      if (aData.status === 'fulfilled') {
        setAnswers(Array.isArray(aData.value?.answers) ? aData.value.answers : []);
      }
      // silently ignore answer history errors — not critical
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (isAuthChecking) return;
    loadData();
  }, [isAuthChecking, loadData]);

  /** Map question text → latest answer object (InterviewAnswerSummary has no question_id) */
  const answerMap = answers.reduce((acc, a) => {
    const key = a.question;
    if (key) acc[key] = a;
    return acc;
  }, {});

  const micIcon = (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"
      strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <line x1="12" y1="19" x2="12" y2="23" />
      <line x1="8" y1="23" x2="16" y2="23" />
    </svg>
  );

  return (
    <PageShell isAuthChecking={isAuthChecking}>
      {/* Breadcrumb */}
      <nav aria-label="Breadcrumb" style={{
        display: 'flex', alignItems: 'center', gap: '0.5rem',
        fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '1.5rem',
      }}>
        <Link href="/applications" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>
          Hồ sơ ứng tuyển
        </Link>
        <span>›</span>
        <Link href={`/applications/${id}`} style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>
          Chi tiết
        </Link>
        <span>›</span>
        <span>Luyện phỏng vấn</span>
      </nav>

      <div className={styles.header}>
        <h1 className={styles.pageTitle}>Luyện phỏng vấn</h1>
        <p className={styles.pageSubtitle}>
          Trả lời từng câu hỏi và nhận phản hồi, đánh giá rủi ro từ AI.
        </p>
        {answers.length > 0 && (
          <span className={styles.historyBadge}>
            {answers.length} câu trả lời trong lịch sử
          </span>
        )}
      </div>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}
      {isLoading && <LoadingSpinner fullPage label="Đang tải câu hỏi…" />}

      {!isLoading && !error && questions.length === 0 && (
        <EmptyStatePage
          icon={micIcon}
          title="Chưa có câu hỏi"
          description="Câu hỏi phỏng vấn sẽ xuất hiện ở đây sau khi phân tích hồ sơ hoàn tất."
        />
      )}

      {!isLoading && questions.length > 0 && (
        <>
          <div className={styles.questionsList}>
            {questions.map((q, i) => {
              const qKey = q.question_id || q.id || String(i);
              const answerKey = q.question || q.text || '';
              return (
                <QuestionItem
                  key={qKey}
                  question={q}
                  index={i}
                  appId={id}
                  pastAnswer={answerMap[answerKey] || null}
                />
              );
            })}
          </div>

          {/* Global disclaimer — always visible */}
          <div className={styles.disclaimer}>
            <Disclaimer text={disclaimer} />
          </div>
        </>
      )}

      {/* Next steps */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', marginTop: '2rem', fontSize: '0.875rem' }}>
        <Link href={`/applications/${id}`} style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>← Quay lại hồ sơ</Link>
        <span style={{ color: 'var(--color-text-muted)' }}>·</span>
        <Link href={`/applications/${id}/cover-letter`} style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>Tiếp tục tới thư xin việc</Link>
        <span style={{ color: 'var(--color-text-muted)' }}>·</span>
        <Link href={`/applications/${id}/package`} style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>Mở bộ hồ sơ</Link>
      </div>
    </PageShell>
  );
}
