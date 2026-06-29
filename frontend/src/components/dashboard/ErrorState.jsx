'use client';

import { useLanguage } from '@/context/LanguageContext';
import styles from '@/styles/ErrorState.module.css';

export default function ErrorState({ message, onRetry }) {
  const { t } = useLanguage();

  return (
    <div className={styles.container} id="error-state">
      <div className={styles.iconWrapper}>
        <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>
      <h3 className={styles.title}>{t('resultV2.error.title')}</h3>
      <p className={styles.description}>
        {message || t('resultV2.error.description')}
      </p>
      {onRetry && (
        <button className={styles.retryButton} onClick={onRetry} id="error-state-retry">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="1 4 1 10 7 10" />
            <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
          </svg>
          {t('resultV2.error.retry')}
        </button>
      )}
    </div>
  );
}
