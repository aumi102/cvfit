'use client';

import Link from 'next/link';
import styles from '@/styles/InterviewRoom.module.css';

export default function PermissionDeniedFallback({ onRetry, fallbackUrl }) {
  return (
    <div className={styles.fallbackCard}>
      <div className={styles.fallbackIcon}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      </div>
      <h2 className={styles.fallbackTitle}>Không thể truy cập thiết bị</h2>
      <p className={styles.fallbackDesc}>
        Chúng tôi cần quyền truy cập microphone để bạn có thể trả lời các câu hỏi phỏng vấn bằng giọng nói. 
        Vui lòng kiểm tra quyền truy cập trong cài đặt trình duyệt của bạn (biểu tượng ổ khóa trên thanh địa chỉ).
      </p>
      <div className={styles.fallbackActions}>
        <button className={styles.btnPrimary} onClick={onRetry}>
          Thử lại
        </button>
        {fallbackUrl && (
          <Link href={fallbackUrl} className={styles.btnOutline}>
            Chuyển sang phỏng vấn bằng văn bản
          </Link>
        )}
      </div>
    </div>
  );
}
