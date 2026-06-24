'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import PageShell from '@/components/common/PageShell';
import ErrorBanner from '@/components/common/ErrorBanner';
import { createTargetJob } from '@/services/targetJobsApi';
import { extractApiError } from '@/utils/errorHelpers';
import { trackEvent, ANALYTICS_EVENTS } from '@/lib/analytics';
import styles from '@/styles/TargetJobs.module.css';

const MAX_JD_CHARS = 8000;

export default function NewJobPage() {
  const { isAuthChecking } = useRequireAuth();
  const router = useRouter();

  const [form, setForm] = useState({
    job_title: '',
    company: '',
    jd_text: '',
    target_role: '',
    source_url: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.job_title.trim() || !form.company.trim()) {
      setError('Vị trí công việc và công ty là bắt buộc.');
      return;
    }
    if (!form.jd_text.trim()) {
      setError('Mô tả công việc là bắt buộc.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const payload = {
        job_title: form.job_title.trim(),
        company: form.company.trim(),
        jd_text: form.jd_text.trim(),
      };
      if (form.target_role.trim()) payload.target_role = form.target_role.trim();
      if (form.source_url.trim()) payload.source_url = form.source_url.trim();

      const job = await createTargetJob(payload);

      trackEvent(ANALYTICS_EVENTS.TARGET_JOB_CREATED, {
        feature_name: 'target_jobs',
        job_status: job?.status || 'saved',
      });

      router.push(`/jobs/${job.id}`);
    } catch (err) {
      const { message, hint } = extractApiError(err, 'Không thể tạo công việc mục tiêu. Vui lòng thử lại.');
      setError(hint ? `${message} — ${hint}` : message);
      setIsSubmitting(false);
    }
  }

  const canSubmit =
    form.job_title.trim() &&
    form.company.trim() &&
    form.jd_text.trim() &&
    !isSubmitting;

  return (
    <PageShell isAuthChecking={isAuthChecking} maxWidth="640px">
      {/* Breadcrumb */}
      <nav className={styles.breadcrumb} aria-label="Breadcrumb">
        <Link href="/jobs">Việc làm mục tiêu</Link>
        <span className={styles.breadcrumbSep}>›</span>
        <span>Công việc mới</span>
      </nav>

      <div className={styles.formCard}>
        <h1 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, color: 'var(--color-text)', marginBottom: '0.375rem' }}>
          Thêm việc làm mục tiêu
        </h1>
        <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: '1.75rem', lineHeight: 1.6 }}>
          Lưu lại một công việc bạn đang nhắm tới. Đính kèm phân tích CV để mở khóa điểm sẵn sàng cá nhân hóa, lộ trình học tập và luyện phỏng vấn.
        </p>

        {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

        <form onSubmit={handleSubmit} id="new-job-form">
          {/* Job Title */}
          <div className={styles.fieldGroup}>
            <label htmlFor="job_title" className={styles.fieldLabel}>
              Vị trí công việc <span style={{ color: 'var(--color-danger)' }}>*</span>
            </label>
            <input
              id="job_title"
              name="job_title"
              type="text"
              required
              value={form.job_title}
              onChange={handleChange}
              disabled={isSubmitting}
              placeholder="ví dụ: Senior Frontend Engineer"
              className={styles.fieldInput}
            />
          </div>

          {/* Company */}
          <div className={styles.fieldGroup}>
            <label htmlFor="company" className={styles.fieldLabel}>
              Công ty <span style={{ color: 'var(--color-danger)' }}>*</span>
            </label>
            <input
              id="company"
              name="company"
              type="text"
              required
              value={form.company}
              onChange={handleChange}
              disabled={isSubmitting}
              placeholder="ví dụ: Google, Shopify, Stripe"
              className={styles.fieldInput}
            />
          </div>

          {/* Target Role (optional) */}
          <div className={styles.fieldGroup}>
            <label htmlFor="target_role" className={styles.fieldLabel}>
              Vị trí mục tiêu <span style={{ color: 'var(--color-text-muted)', fontWeight: 400, textTransform: 'none' }}>(không bắt buộc — ghi đè vị trí công việc khi phân tích)</span>
            </label>
            <input
              id="target_role"
              name="target_role"
              type="text"
              value={form.target_role}
              onChange={handleChange}
              disabled={isSubmitting}
              placeholder="ví dụ: Frontend Engineer"
              className={styles.fieldInput}
            />
          </div>

          {/* Source URL (optional) */}
          <div className={styles.fieldGroup}>
            <label htmlFor="source_url" className={styles.fieldLabel}>
              URL bài đăng tuyển <span style={{ color: 'var(--color-text-muted)', fontWeight: 400, textTransform: 'none' }}>(không bắt buộc)</span>
            </label>
            <input
              id="source_url"
              name="source_url"
              type="url"
              value={form.source_url}
              onChange={handleChange}
              disabled={isSubmitting}
              placeholder="https://…"
              className={styles.fieldInput}
            />
          </div>

          {/* JD Text */}
          <div className={styles.fieldGroup}>
            <label htmlFor="jd_text" className={styles.fieldLabel}>
              Mô tả công việc <span style={{ color: 'var(--color-danger)' }}>*</span>
            </label>
            <textarea
              id="jd_text"
              name="jd_text"
              value={form.jd_text}
              onChange={handleChange}
              disabled={isSubmitting}
              maxLength={MAX_JD_CHARS}
              placeholder="Dán toàn bộ mô tả công việc vào đây…"
              className={`${styles.fieldInput} ${styles.fieldTextarea}`}
            />
            <div className={styles.charCount}>
              {form.jd_text.length}/{MAX_JD_CHARS}
            </div>
          </div>

          <div className={styles.formActions}>
            <Link href="/jobs" className={styles.btnSecondary}>
              Hủy
            </Link>
            <button
              type="submit"
              className={styles.btnPrimary}
              disabled={!canSubmit}
              id="submit-job-btn"
            >
              {isSubmitting ? (
                <>
                  <span style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%', animation: 'spin 0.7s linear infinite', display: 'inline-block' }} />
                  Đang lưu…
                </>
              ) : 'Lưu công việc mục tiêu'}
            </button>
          </div>
        </form>
      </div>
    </PageShell>
  );
}
