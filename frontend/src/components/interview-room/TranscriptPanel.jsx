'use client';

import { useEffect, useRef } from 'react';
import styles from '@/styles/InterviewRoom.module.css';

export default function TranscriptPanel({ transcript = [] }) {
  const scrollRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [transcript]);

  const formatTime = (timestamp) => {
    // Transcript timestamps are local display metadata, not recorded audio.
    const d = new Date(timestamp);
    if (isNaN(d.getTime())) return '';
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
  };

  return (
    <div className={styles.transcriptPanel}>
      <div className={styles.transcriptHeader}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        Bản ghi thoại trực tiếp
      </div>
      
      <div className={styles.transcriptBody} ref={scrollRef}>
        {transcript.length === 0 ? (
          <div className={styles.transcriptEmpty}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
              <line x1="12" y1="19" x2="12" y2="23" />
              <line x1="8" y1="23" x2="16" y2="23" />
            </svg>
            <p>Bản ghi thoại sẽ xuất hiện ở đây khi buổi phỏng vấn bắt đầu.</p>
          </div>
        ) : (
          transcript.map((entry) => (
            <div key={entry.id} className={styles.transcriptEntry}>
              <div className={`${styles.transcriptAvatar} ${entry.speaker === 'ai' ? styles['transcriptAvatar--ai'] : styles['transcriptAvatar--user']}`}>
                {entry.speaker === 'ai' ? 'AI' : 'Bạn'}
              </div>
              <div className={styles.transcriptBubble}>
                <div className={styles.transcriptSpeaker}>
                  {entry.speaker === 'ai' ? 'Nhà tuyển dụng AI' : 'Bạn'}
                </div>
                <div className={styles.transcriptText}>
                  {entry.text}
                </div>
                {entry.timestamp > 0 && (
                  <div className={styles.transcriptTime}>
                    {formatTime(entry.timestamp)}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
