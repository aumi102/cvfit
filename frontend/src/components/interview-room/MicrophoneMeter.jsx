'use client';

import styles from '@/styles/InterviewRoom.module.css';

export default function MicrophoneMeter({ level, isMuted }) {
  // Normalize level (0-1) to number of bars to fill (0-5)
  const numBars = 5;
  const activeBars = isMuted ? 0 : Math.ceil(level * numBars);

  return (
    <div className={styles.micMeter}>
      <div className={styles.micMeterBars}>
        {Array.from({ length: numBars }).map((_, i) => {
          const isActive = i < activeBars;
          const height = isActive ? 100 : 20; // %
          
          return (
            <div 
              key={i} 
              className={`${styles.micMeterBar} ${isMuted ? styles['micMeterBar--muted'] : ''}`}
              style={{ height: `${height}%`, opacity: isActive ? 1 : 0.3 }}
            />
          );
        })}
      </div>
      <div className={styles.micMeterLabel}>
        {isMuted ? 'Đã tắt mic' : 'Microphone'}
      </div>
    </div>
  );
}
