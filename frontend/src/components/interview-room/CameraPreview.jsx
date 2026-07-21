'use client';

import { useEffect, useRef } from 'react';
import styles from '@/styles/InterviewRoom.module.css';

export default function CameraPreview({ stream, isOff, isMuted }) {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  return (
    <div className={styles.cameraCard}>
      {isOff || !stream ? (
        <div className={styles.cameraOff}>
          <div className={styles.cameraOffIcon}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M23 7l-7 5 7 5V7z" opacity="0.3"></path>
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2" opacity="0.3"></rect>
              <line x1="2" y1="2" x2="22" y2="22"></line>
            </svg>
          </div>
        </div>
      ) : (
        <video 
          ref={videoRef}
          autoPlay 
          playsInline 
          muted 
          className={styles.cameraVideo}
        />
      )}
      
      {isMuted && (
        <div className={styles.cameraBadge} style={{ background: 'rgba(239, 68, 68, 0.8)' }}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="1" y1="1" x2="23" y2="23"></line>
            <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"></path>
            <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"></path>
            <line x1="12" y1="19" x2="12" y2="23"></line>
            <line x1="8" y1="23" x2="16" y2="23"></line>
          </svg>
          Đang tắt mic
        </div>
      )}
    </div>
  );
}
