'use client';

import styles from '@/styles/InterviewRoom.module.css';

export default function LoadingOverlay() {
  return (
    <div className={styles.loadingOverlay}>
      <div className={styles.loadingIcon}>
        AI
      </div>
      <div className={styles.loadingText}>
        Đang kết nối với AI Interviewer...
      </div>
      <div className={styles.loadingSubtext}>
        Vui lòng đợi trong giây lát
      </div>
      <div className={styles.loadingDots}>
        <div className={styles.loadingDot} />
        <div className={styles.loadingDot} />
        <div className={styles.loadingDot} />
      </div>
    </div>
  );
}
