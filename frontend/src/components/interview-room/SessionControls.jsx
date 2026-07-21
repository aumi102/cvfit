'use client';

import { useState } from 'react';
import styles from '@/styles/InterviewRoom.module.css';

export default function SessionControls({ 
  isMuted, 
  isCameraOff, 
  onToggleMute, 
  onToggleCamera, 
  onEndSession 
}) {
  const [showConfirm, setShowConfirm] = useState(false);

  return (
    <>
      <div className={styles.controlsBar}>
        <button 
          className={`${styles.controlBtn} ${isMuted ? styles['controlBtn--danger'] : ''}`}
          onClick={onToggleMute}
          title={isMuted ? "Bật mic" : "Tắt mic"}
        >
          {isMuted ? (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="1" y1="1" x2="23" y2="23"></line>
              <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"></path>
              <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"></path>
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
          )}
          <span>{isMuted ? 'Bật Mic' : 'Tắt Mic'}</span>
        </button>

        <button 
          className={`${styles.controlBtn} ${isCameraOff ? styles['controlBtn--danger'] : ''}`}
          onClick={onToggleCamera}
          title={isCameraOff ? "Bật camera" : "Tắt camera"}
        >
          {isCameraOff ? (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M23 7l-7 5 7 5V7z" opacity="0.3"></path>
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2" opacity="0.3"></rect>
              <line x1="2" y1="2" x2="22" y2="22"></line>
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M23 7l-7 5 7 5V7z"></path>
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
            </svg>
          )}
          <span>{isCameraOff ? 'Bật Camera' : 'Tắt Camera'}</span>
        </button>

        <div className={styles.controlDivider} />

        <button 
          className={`${styles.controlBtn} ${styles['controlBtn--danger']}`}
          onClick={() => setShowConfirm(true)}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <line x1="9" y1="9" x2="15" y2="15" />
            <line x1="15" y1="9" x2="9" y2="15" />
          </svg>
          <span>Kết thúc</span>
        </button>
      </div>

      {showConfirm && (
        <div className={styles.confirmOverlay}>
          <div className={styles.confirmCard}>
            <h3 className={styles.confirmTitle}>Kết thúc phỏng vấn?</h3>
            <p className={styles.confirmText}>
              Bạn có chắc chắn muốn kết thúc buổi phỏng vấn này không? Dữ liệu của bạn sẽ được AI tổng hợp và phân tích ngay lập tức.
            </p>
            <div className={styles.confirmActions}>
              <button className={styles.btnSecondary} onClick={() => setShowConfirm(false)}>
                Hủy
              </button>
              <button 
                className={`${styles.btnPrimary} ${styles['controlBtn--danger']}`} 
                onClick={() => {
                  setShowConfirm(false);
                  onEndSession();
                }}
              >
                Kết thúc ngay
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
