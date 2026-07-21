'use client';

import { useState } from 'react';
import styles from '@/styles/InterviewRoom.module.css';

export default function DevicePermissionCheck({ 
  micStatus, 
  camStatus, 
  onRequestMic, 
  onRequestCam, 
  onNext, 
  onCancel,
  isCameraOff
}) {
  const [consentChecked, setConsentChecked] = useState(false);
  const [useCamera, setUseCamera] = useState(!isCameraOff);
  const [isRequesting, setIsRequesting] = useState(false);

  const handleRequestPermissions = async () => {
    setIsRequesting(true);
    try {
      await onRequestMic();
      if (useCamera) {
        await onRequestCam();
      }
    } finally {
      setIsRequesting(false);
    }
  };

  const isMicReady = micStatus === 'granted';
  const isCamReady = !useCamera || camStatus === 'granted';
  const canProceed = isMicReady && isCamReady && consentChecked;

  const renderStatusBadge = (status) => {
    switch(status) {
      case 'granted':
        return <span className={`${styles.permissionStatus} ${styles['permissionStatus--granted']}`}>Đã cấp quyền</span>;
      case 'denied':
        return <span className={`${styles.permissionStatus} ${styles['permissionStatus--denied']}`}>Bị từ chối</span>;
      default:
        return <span className={`${styles.permissionStatus} ${styles['permissionStatus--prompt']}`}>Cần cấp quyền</span>;
    }
  };

  return (
    <div className={styles.formCard}>
      <h1 className={styles.formTitle}>Thiết lập thiết bị</h1>
      <p className={styles.formSubtitle}>
        Vui lòng cấp quyền truy cập microphone và camera (tùy chọn) để bắt đầu phiên phỏng vấn.
        Tất cả dữ liệu âm thanh/hình ảnh được xử lý trực tiếp và không lưu trữ trên máy chủ sau buổi phỏng vấn.
      </p>

      {/* Settings Toggles */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
        <div className={styles.toggleRow}>
          <div>
            <div className={styles.toggleLabel}>Sử dụng Camera</div>
            <div className={styles.toggleDesc}>Giao tiếp qua video (Khuyên dùng)</div>
          </div>
          <button 
            type="button" 
            className={`${styles.toggleSwitch} ${useCamera ? styles['toggleSwitch--on'] : ''}`}
            onClick={() => setUseCamera(!useCamera)}
          >
            <div className={styles.toggleSwitchKnob} />
          </button>
        </div>
      </div>

      <div className={styles.permissionGrid}>
        {/* Microphone Card */}
        <div className={`${styles.permissionCard} ${micStatus === 'granted' ? styles['permissionCard--granted'] : micStatus === 'denied' ? styles['permissionCard--denied'] : ''}`}>
          <div className={styles.permissionIcon}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
          </div>
          <div className={styles.permissionTitle}>Microphone</div>
          {renderStatusBadge(micStatus)}
          
          {micStatus === 'prompt' && (
            <p className={styles.permissionHelp}>Cần thiết để AI có thể nghe câu trả lời của bạn.</p>
          )}
          {micStatus === 'denied' && (
            <p className={styles.permissionHelp}>Vui lòng cho phép truy cập microphone trong cài đặt trình duyệt của bạn (biểu tượng ổ khóa trên thanh địa chỉ).</p>
          )}
        </div>

        {/* Camera Card */}
        {useCamera && (
          <div className={`${styles.permissionCard} ${camStatus === 'granted' ? styles['permissionCard--granted'] : camStatus === 'denied' ? styles['permissionCard--denied'] : ''}`}>
            <div className={styles.permissionIcon}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M23 7l-7 5 7 5V7z"></path>
                <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
              </svg>
            </div>
            <div className={styles.permissionTitle}>Camera</div>
            {renderStatusBadge(camStatus)}
            
            {camStatus === 'prompt' && (
              <p className={styles.permissionHelp}>Tùy chọn: giúp buổi phỏng vấn chân thực hơn.</p>
            )}
            {camStatus === 'denied' && (
              <p className={styles.permissionHelp}>Vui lòng cho phép truy cập camera trong cài đặt trình duyệt của bạn.</p>
            )}
          </div>
        )}
      </div>

      {(!isMicReady || (!isCamReady && useCamera)) && (
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <button 
            type="button" 
            className={styles.permissionBtn} 
            onClick={handleRequestPermissions}
            disabled={isRequesting}
          >
            {isRequesting ? 'Đang yêu cầu quyền...' : 'Cấp quyền truy cập'}
          </button>
        </div>
      )}

      {/* Consent */}
      <div className={styles.consentRow}>
        <input 
          type="checkbox" 
          id="consent-check" 
          className={styles.consentCheckbox}
          checked={consentChecked}
          onChange={(e) => setConsentChecked(e.target.checked)}
        />
        <label htmlFor="consent-check" className={styles.consentText}>
          Tôi đồng ý cho phép sử dụng microphone {useCamera && 'và camera'} để ghi nhận và phân tích trong suốt buổi phỏng vấn. Tôi hiểu rằng tôi có thể dừng phiên bất kỳ lúc nào.
        </label>
      </div>

      {/* Actions */}
      <div className={styles.formActions}>
        <button type="button" className={styles.btnSecondary} onClick={onCancel}>
          Trở lại
        </button>
        <button 
          type="button" 
          className={styles.btnPrimary} 
          onClick={onNext}
          disabled={!canProceed}
        >
          Hoàn tất thiết lập
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: 4 }}>
            <path d="M5 12h14" />
            <path d="m12 5 7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  );
}
