'use client';

import { useLanguage } from '@/context/LanguageContext';
import { trackEvent, ANALYTICS_EVENTS } from '@/lib/analytics';
import styles from '@/styles/LanguageSwitcher.module.css';

export default function LanguageSwitcher() {
  const { lang, changeLanguage } = useLanguage();

  const handleSwitch = (next) => {
    if (next !== lang) {
      trackEvent(ANALYTICS_EVENTS.LANGUAGE_SWITCH, { feature_name: 'i18n', language: next });
    }
    changeLanguage(next);
  };

  return (
    <div className={styles.toggleContainer}>
      <button
        className={`${styles.toggleBtn} ${lang === 'vi' ? styles.active : ''}`}
        onClick={() => handleSwitch('vi')}
        aria-label="Tiếng Việt"
      >
        VI
      </button>
      <button
        className={`${styles.toggleBtn} ${lang === 'en' ? styles.active : ''}`}
        onClick={() => handleSwitch('en')}
        aria-label="English"
      >
        EN
      </button>
    </div>
  );
}
