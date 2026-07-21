'use client';

import styles from '@/styles/InterviewRoom.module.css';

export default function InterviewSkeleton() {
  return (
    <div className={styles.skeletonRoom}>
      <div className={styles.roomLeft}>
        <div className={styles.skeletonBlock} style={{ height: 200 }}>
          <div className={styles.skeletonShimmer} />
        </div>
        <div className={styles.skeletonBlock} style={{ height: 60 }}>
          <div className={styles.skeletonShimmer} />
        </div>
      </div>
      
      <div className={styles.roomCenter}>
        <div className={styles.skeletonBlock} style={{ height: 80 }}>
          <div className={styles.skeletonShimmer} />
        </div>
        <div className={styles.skeletonBlock} style={{ flex: 1, minHeight: 300 }}>
          <div className={styles.skeletonShimmer} />
        </div>
      </div>
      
      <div className={styles.roomRight}>
        <div className={styles.skeletonBlock} style={{ height: '100%' }}>
          <div className={styles.skeletonShimmer} />
        </div>
      </div>
    </div>
  );
}
