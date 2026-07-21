'use client';

import { useLanguage } from '@/context/LanguageContext';
import styles from '@/styles/EmptyState.module.css';

export default function EmptyState({ onRetry }) {
  const { t } = useLanguage();

  return (
    <div className={styles.container} id="empty-state">
      <div className={styles.iconWrapper}>
        <svg className={styles.icon} viewBox="0 0 80 80" fill="none">
          <circle cx="40" cy="40" r="38" stroke="currentColor" strokeWidth="2" strokeDasharray="6 4" opacity="0.3" />
          <circle cx="40" cy="40" r="24" stroke="currentColor" strokeWidth="2" opacity="0.15" />
          <path
            d="M40 28v12M40 48h.01"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            opacity="0.6"
          />
          <path
            d="M28 52c2.5-4 6.8-6 12-6s9.5 2 12 6"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            opacity="0.4"
          />
        </svg>
      </div>
      <h3 className={styles.title}>{t('resultV2.empty.title')}</h3>
      <p className={styles.description}>{t('resultV2.empty.description')}</p>
      {onRetry && (
        <button className={styles.retryButton} onClick={onRetry} id="empty-state-retry">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="1 4 1 10 7 10" />
            <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
          </svg>
          {t('resultV2.empty.retry')}
        </button>
      )}
    </div>
  );
}
