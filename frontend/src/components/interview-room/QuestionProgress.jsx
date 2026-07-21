'use client';

import styles from '@/styles/InterviewRoom.module.css';

export default function QuestionProgress({ currentIndex, total }) {
  if (total === 0) return null;

  const percent = total > 0 ? ((currentIndex + 1) / total) * 100 : 0;

  return (
    <div className={styles.questionProgress}>
      <div className={styles.progressLabel}>
        Câu {currentIndex + 1} / {total}
      </div>
      
      <div className={styles.progressTrack}>
        <div 
          className={styles.progressFill} 
          style={{ width: `${Math.min(100, Math.max(0, percent))}%` }} 
        />
      </div>

      <div className={styles.progressDots}>
        {Array.from({ length: total }).map((_, i) => (
          <div 
            key={i} 
            className={`${styles.progressDot} ${i < currentIndex ? styles['progressDot--done'] : i === currentIndex ? styles['progressDot--current'] : ''}`}
          />
        ))}
      </div>
    </div>
  );
}
