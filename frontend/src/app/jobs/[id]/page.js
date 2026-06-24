'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import PageShell from '@/components/common/PageShell';
import ErrorBanner from '@/components/common/ErrorBanner';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { getTargetJob, updateTargetJob } from '@/services/targetJobsApi';
import { extractApiError } from '@/utils/errorHelpers';
import { trackEvent, ANALYTICS_EVENTS } from '@/lib/analytics';
import styles from '@/styles/TargetJobs.module.css';

const JOB_STATUSES = [
  { value: 'saved', label: 'Đã lưu' },
  { value: 'analyzing', label: 'Đang phân tích' },
  { value: 'ready_to_apply', label: 'Sẵn sàng ứng tuyển' },
  { value: 'interviewing', label: 'Đang phỏng vấn' },
  { value: 'applied', label: 'Đã ứng tuyển' },
  { value: 'rejected', label: 'Bị từ chối' },
  { value: 'offer', label: 'Đề nghị làm việc (Offer)' },
  { value: 'archived', label: 'Đã lưu trữ' },
];

function formatDate(value) {
  if (!value) return '—';
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? '—' : d.toLocaleDateString();
}

function getInitial(name) {
  return (name || '?').charAt(0).toUpperCase();
}

function StatusBadge({ status }) {
  const cls = styles[`status--${status}`] || styles['status--saved'];
  return (
    <span className={`${styles.statusBadge} ${cls}`}>
      {status?.replace(/_/g, ' ') || 'đã lưu'}
    </span>
  );
}

export default function JobDetailPage() {
  const { isAuthChecking } = useRequireAuth();
  const { id } = useParams();

  const [job, setJob] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [statusSuccess, setStatusSuccess] = useState(false);

  const loadJob = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getTargetJob(id);
      setJob(data);
    } catch (err) {
      const { message } = extractApiError(err, 'Không thể tải chi tiết công việc.');
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (isAuthChecking) return;
    loadJob();
  }, [isAuthChecking, loadJob]);

  const handleStatusChange = async (newStatus) => {
    if (!job || newStatus === job.status) return;
    setIsUpdatingStatus(true);
    setStatusSuccess(false);
    try {
      const updated = await updateTargetJob(id, { status: newStatus });
      setJob(updated);
      setStatusSuccess(true);
      trackEvent(ANALYTICS_EVENTS.TARGET_JOB_STATUS_CHANGED, {
        feature_name: 'target_jobs',
        job_status: newStatus,
      });
      setTimeout(() => setStatusSuccess(false), 2500);
    } catch (err) {
      const { message } = extractApiError(err, 'Không thể cập nhật trạng thái.');
      setError(message);
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  return (
    <PageShell isAuthChecking={isAuthChecking} maxWidth="960px">
      {/* Breadcrumb */}
      <nav className={styles.breadcrumb} aria-label="Breadcrumb">
        <Link href="/jobs">Việc làm mục tiêu</Link>
        <span className={styles.breadcrumbSep}>›</span>
        <span>{job ? `${job.company} — ${job.job_title}` : 'Đang tải…'}</span>
      </nav>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}
      {isLoading && <LoadingSpinner fullPage label="Đang tải chi tiết công việc…" />}

      {!isLoading && job && (
        <>
          {/* Hero Card */}
          <div className={styles.heroCard}>
            <div className={styles.heroTop}>
              <div className={styles.companyLogo} aria-hidden="true">
                {getInitial(job.company)}
              </div>
              <div className={styles.heroInfo}>
                <h1 className={styles.heroCompany}>{job.company || 'Công ty không xác định'}</h1>
                <p className={styles.heroRole}>{job.job_title || 'Vị trí không tên'}</p>
                {job.target_role && (
                  <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)', marginTop: 2 }}>
                    Mục tiêu: {job.target_role}
                  </p>
                )}
              </div>
              <div className={styles.heroActions}>
                {/* Status Change */}
                <select
                  className={styles.statusSelect}
                  value={job.status || 'saved'}
                  onChange={(e) => handleStatusChange(e.target.value)}
                  disabled={isUpdatingStatus}
                  id="job-status-select"
                  title="Thay đổi trạng thái"
                >
                  {JOB_STATUSES.map((s) => (
                    <option key={s.value} value={s.value}>{s.label}</option>
                  ))}
                </select>
                {statusSuccess && (
                  <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-success)', fontWeight: 600 }}>
                    ✓ Đã cập nhật
                  </span>
                )}
              </div>
            </div>

            <div className={styles.infoGrid}>
              <div className={styles.infoItem}>
                <label>Trạng thái</label>
                <StatusBadge status={job.status} />
              </div>
              <div className={styles.infoItem}>
                <label>Đã thêm</label>
                <span>{formatDate(job.created_at)}</span>
              </div>
              {job.readiness_score != null && (
                <div className={styles.infoItem}>
                  <label>Điểm sẵn sàng</label>
                  <span style={{ color: 'var(--color-primary)', fontWeight: 700, fontSize: 'var(--font-size-lg)' }}>
                    {job.readiness_score}%
                  </span>
                </div>
              )}
              {job.source_url && (
                <div className={styles.infoItem}>
                  <label>Nguồn</label>
                  <a href={job.source_url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--color-primary)', fontSize: 'var(--font-size-sm)', wordBreak: 'break-all' }}>
                    Xem tin tuyển dụng ↗
                  </a>
                </div>
              )}
            </div>
          </div>

          {/* Readiness Score Section */}
          {job.readiness_score != null && (
            <div className={styles.sectionCard}>
              <div className={styles.sectionTitle}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                </svg>
                Điểm sẵn sàng
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
                <div style={{ fontSize: '3.5rem', fontWeight: 800, color: 'var(--color-primary)', letterSpacing: '-0.04em', lineHeight: 1 }}>
                  {job.readiness_score}%
                </div>
                <div style={{ flex: 1, minWidth: 200 }}>
                  <div style={{ height: 12, background: 'var(--color-border)', borderRadius: 'var(--radius-full)', overflow: 'hidden', marginBottom: '0.5rem' }}>
                    <div style={{
                      height: '100%',
                      width: `${job.readiness_score}%`,
                      background: 'linear-gradient(90deg, var(--color-primary), #8B5CF6)',
                      borderRadius: 'var(--radius-full)',
                      transition: 'width 1s ease-out',
                    }} />
                  </div>
                  <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
                    Dựa trên phân tích CV của bạn so với mô tả công việc này
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Attached Analysis */}
          <div className={styles.sectionCard}>
            <div className={styles.sectionTitle}>
              🔗 Phân tích đính kèm
              {job.best_analysis_job_id && (
                <span style={{ marginLeft: 'auto', fontSize: 'var(--font-size-xs)', background: 'var(--color-success-light)', color: '#065F46', padding: '2px 8px', borderRadius: 'var(--radius-full)', fontWeight: 600 }}>
                  ✓ Đã đính kèm
                </span>
              )}
            </div>
            {job.best_analysis_job_id ? (
              <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                Phân tích đã được đính kèm. Bạn có thể tạo câu hỏi phỏng vấn, thư xin việc và toàn bộ hồ sơ ứng tuyển.
              </p>
            ) : (
              <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                Chưa đính kèm phân tích nào.{' '}
                <Link href="/dashboard" style={{ color: 'var(--color-primary)' }}>Chạy phân tích CV</Link>{' '}
                và đính kèm nó để mở khóa điểm sẵn sàng, nhiệm vụ học tập và luyện phỏng vấn.
              </p>
            )}

            {/* Application Package CTA */}
            {job.best_analysis_job_id && job.application_id && (
              <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem', flexWrap: 'wrap' }}>
                <Link
                  href={`/applications/${job.application_id}/package`}
                  className={styles.btnPrimary}
                  id="job-package-btn"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                  </svg>
                  Bộ hồ sơ ứng tuyển
                </Link>
                <Link
                  href={`/applications/${job.application_id}/interview`}
                  className={styles.btnSecondary}
                >
                  Luyện phỏng vấn
                </Link>
                <Link
                  href={`/applications/${job.application_id}/cover-letter`}
                  className={styles.btnSecondary}
                >
                  Thư xin việc
                </Link>
              </div>
            )}
          </div>

          {/* Learning & Interview Quick Links */}
          <div className={styles.sectionCard}>
            <div className={styles.sectionTitle}>
              📚 Bước tiếp theo
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {[
                { href: '/learning', label: 'Lộ trình học tập' },
                { href: '/interview/sessions/new', label: 'Luyện phỏng vấn' },
                { href: '/dashboard', label: 'Chạy phân tích CV' },
                { href: '/help/assistant', label: 'Nhận trợ giúp' },
              ].map((step) => (
                <Link
                  key={step.label}
                  href={step.href}
                  style={{
                    padding: '0.35rem 0.8rem',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-full)',
                    color: 'var(--color-primary)',
                    textDecoration: 'none',
                    fontWeight: 600,
                    fontSize: 'var(--font-size-sm)',
                  }}
                >
                  {step.label}
                </Link>
              ))}
            </div>
          </div>

          {/* JD Preview */}
          {job.jd_text && (
            <div className={styles.sectionCard}>
              <div className={styles.sectionTitle}>📄 Mô tả công việc</div>
              <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.8, whiteSpace: 'pre-wrap', maxHeight: 300, overflow: 'auto' }}>
                {job.jd_text}
              </p>
            </div>
          )}
        </>
      )}
    </PageShell>
  );
}
