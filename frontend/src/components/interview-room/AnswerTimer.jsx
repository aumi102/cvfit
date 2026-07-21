'use client';

import { formatTime } from '@/lib/interviewTypes';
import styles from '@/styles/InterviewRoom.module.css';

export default function AnswerTimer({ seconds }) {
  // Logic to highlight long answers
  const isWarning = seconds > 120; // 2 mins
  const isDanger = seconds > 180;  // 3 mins

  const valClass = isDanger ? styles['timerValue--danger'] : isWarning ? styles['timerValue--warning'] : '';

  return (
    <div className={styles.answerTimer}>
      <div className={styles.timerIcon}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
      </div>
      <div className={`${styles.timerValue} ${valClass}`}>
        {formatTime(seconds)}
      </div>
    </div>
  );
}
