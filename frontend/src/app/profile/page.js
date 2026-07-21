'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import PageShell from '@/components/common/PageShell';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ErrorBanner from '@/components/common/ErrorBanner';
import { getProfile } from '@/services/profileApi';
import { getStoredUser } from '@/services/authStorage';
import { extractApiError } from '@/utils/errorHelpers';
import styles from '@/styles/Profile.module.css';

export default function ProfilePage() {
  const { isAuthChecking, user: authUser } = useRequireAuth();
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Get user from local storage as a fallback
  const storedUser = typeof window !== 'undefined' ? getStoredUser() : null;
  const displayUser = authUser || storedUser;

  useEffect(() => {
    if (isAuthChecking) return;
    let active = true;
    setIsLoading(true);
    setError(null);

    (async () => {
      try {
        const data = await getProfile();
        if (!active) return;
        setProfile(data);
      } catch (err) {
        if (!active) return;
        // Profile endpoint may not exist yet — gracefully degrade
        if (err?.response?.status !== 404) {
          const { message } = extractApiError(err, 'Không thể tải hồ sơ.');
          setError(message);
        }
      } finally {
        if (active) setIsLoading(false);
      }
    })();

    return () => { active = false; };
  }, [isAuthChecking]);

  const name = displayUser?.full_name || displayUser?.email || 'Người dùng';
  const initial = name.charAt(0).toUpperCase();

  return (
    <PageShell isAuthChecking={isAuthChecking}>
      <h1 className={styles.pageTitle}>Hồ sơ nghề nghiệp</h1>
      <p className={styles.pageSubtitle}>Hồ sơ chuyên môn và kho bằng chứng của bạn.</p>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      {isLoading ? (
        <LoadingSpinner fullPage label="Đang tải hồ sơ…" />
      ) : (
        <>
          {/* Profile card */}
          <div className={styles.profileCard}>
            <div className={styles.profileHeader}>
              <div className={styles.avatar} aria-hidden="true">{initial}</div>
              <div>
                <p className={styles.profileName}>{name}</p>
                {displayUser?.email && (
                  <p className={styles.profileEmail}>{displayUser.email}</p>
                )}
              </div>
            </div>

            {/* Stats row */}
            <div className={styles.statsGrid}>
              <div className={styles.stat}>
                <div className={styles.statValue}>
                  {profile?.applications_count ?? '—'}
                </div>
                <div className={styles.statLabel}>Hồ sơ ứng tuyển</div>
              </div>
              <div className={styles.stat}>
                <div className={styles.statValue}>
                  {profile?.avg_fit_score != null
                    ? `${Math.round(profile.avg_fit_score)}%`
                    : '—'}
                </div>
                <div className={styles.statLabel}>Điểm phù hợp TB</div>
              </div>
              <div className={styles.stat}>
                <div className={styles.statValue}>
                  {profile?.evidence_count ?? '—'}
                </div>
                <div className={styles.statLabel}>Bằng chứng</div>
              </div>
              <div className={styles.stat}>
                <div className={styles.statValue}>
                  {profile?.interviews_completed ?? '—'}
                </div>
                <div className={styles.statLabel}>Phỏng vấn hoàn thành</div>
              </div>
            </div>
          </div>

          {/* Quick links */}
          <div className={styles.quickLinks}>
            <Link href="/profile/evidence" className={styles.quickLink} id="go-to-evidence-btn">
              <div className={styles.quickLinkIcon} style={{ background: '#EFF6FF' }}>
                🗂️
              </div>
              <div>
                <p className={styles.quickLinkTitle}>Kho bằng chứng</p>
                <p className={styles.quickLinkDesc}>Quản lý kỹ năng, dự án & thành tích</p>
              </div>
            </Link>
            <Link href="/applications" className={styles.quickLink}>
              <div className={styles.quickLinkIcon} style={{ background: '#F0FDF4' }}>
                📋
              </div>
              <div>
                <p className={styles.quickLinkTitle}>Hồ sơ ứng tuyển</p>
                <p className={styles.quickLinkDesc}>Xem tất cả hồ sơ ứng tuyển của bạn</p>
              </div>
            </Link>
            <Link href="/history" className={styles.quickLink}>
              <div className={styles.quickLinkIcon} style={{ background: '#FEF3C7' }}>
                📊
              </div>
              <div>
                <p className={styles.quickLinkTitle}>Lịch sử phân tích</p>
                <p className={styles.quickLinkDesc}>Tất cả kết quả phân tích CV</p>
              </div>
            </Link>
            <Link href="/dashboard" className={styles.quickLink}>
              <div className={styles.quickLinkIcon} style={{ background: '#F5F3FF' }}>
                ⚡
              </div>
              <div>
                <p className={styles.quickLinkTitle}>Phân tích mới</p>
                <p className={styles.quickLinkDesc}>Chạy phân tích CV mới</p>
              </div>
            </Link>
          </div>
        </>
      )}
    </PageShell>
  );
}
