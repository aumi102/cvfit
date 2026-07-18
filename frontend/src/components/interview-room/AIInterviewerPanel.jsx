'use client';

import styles from '@/styles/InterviewRoom.module.css';

export default function AIInterviewerPanel({ 
  currentQuestion, 
  isAISpeaking, 
  isUserSpeaking 
}) {
  return (
    <div className={styles.centerPanel}>
      <div className={styles.aiPanel}>
        <div className={styles.aiAvatar}>
          AI
          <div className={`${styles.aiAvatarRing} ${isAISpeaking ? styles['aiAvatarRing--speaking'] : ''}`} />
        </div>
        
        <div className={styles.aiName}>AI Interviewer</div>
        <div className={styles.aiRole}>Chuyên gia tuyển dụng</div>

        <div className={styles.aiSpeakingIndicator} style={{ opacity: isAISpeaking ? 1 : 0, transition: 'opacity 0.2s' }}>
          <div className={styles.voiceWave}>
            <div className={styles.voiceWaveBar} />
            <div className={styles.voiceWaveBar} />
            <div className={styles.voiceWaveBar} />
            <div className={styles.voiceWaveBar} />
            <div className={styles.voiceWaveBar} />
          </div>
          <span>Đang nói...</span>
        </div>
      </div>

      {currentQuestion && (
        <div className={styles.questionDisplay}>
          <div className={styles.questionDisplayLabel}>Câu hỏi hiện tại</div>
          <div className={styles.questionDisplayText}>
            {currentQuestion.text}
          </div>
          
          {isUserSpeaking && (
            <div className={`${styles.speakingIndicator} ${styles['speakingIndicator--user']}`}>
              <div className={styles.voiceWave} style={{ height: 12 }}>
                <div className={styles.voiceWaveBar} style={{ background: 'var(--color-primary)' }}/>
                <div className={styles.voiceWaveBar} style={{ background: 'var(--color-primary)' }}/>
                <div className={styles.voiceWaveBar} style={{ background: 'var(--color-primary)' }}/>
              </div>
              <span>Bạn đang trả lời...</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
