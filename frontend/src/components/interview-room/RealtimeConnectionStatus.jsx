'use client';

import styles from '@/styles/InterviewRoom.module.css';
import { CONNECTION_STATUS } from '@/lib/interviewTypes';

export default function RealtimeConnectionStatus({ status }) {
  const getStatusDisplay = () => {
    switch (status) {
      case CONNECTION_STATUS.CONNECTED:
        return { label: 'Đã kết nối', dotClass: styles['connectionDot--connected'] };
      case CONNECTION_STATUS.CONNECTING:
        return { label: 'Đang kết nối...', dotClass: styles['connectionDot--connecting'] };
      case CONNECTION_STATUS.RECONNECTING:
        return { label: 'Đang kết nối lại...', dotClass: styles['connectionDot--reconnecting'] };
      case CONNECTION_STATUS.DISCONNECTED:
        return { label: 'Đã ngắt kết nối', dotClass: styles['connectionDot--disconnected'] };
      case CONNECTION_STATUS.FAILED:
        return { label: 'Lỗi kết nối', dotClass: styles['connectionDot--failed'] };
      default:
        return { label: 'Đang chuẩn bị', dotClass: styles['connectionDot--idle'] };
    }
  };

  const display = getStatusDisplay();

  return (
    <div className={styles.connectionStatus}>
      <div className={`${styles.connectionDot} ${display.dotClass}`} />
      <span className={styles.connectionText}>{display.label}</span>
    </div>
  );
}
