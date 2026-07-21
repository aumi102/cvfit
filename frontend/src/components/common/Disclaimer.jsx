'use client';

import styles from '@/styles/PageShell.module.css';

/**
 * Disclaimer
 * Always-visible disclaimer block. Never collapsed, never hidden.
 * Renders backend disclaimer text or a default message.
 *
 * @param {{ text?: string, title?: string }} props
 */
export default function Disclaimer({ text, title = 'Lưu ý quan trọng' }) {
  const content =
    text ||
    'Nội dung này được AI tạo ra và chỉ mang tính tham khảo. ' +
      'Không nên coi đây là tư vấn chuyên môn. ' +
      'Luôn xác minh thông tin độc lập trước khi đưa ra quyết định nghề nghiệp.';

  return (
    <aside className={styles.disclaimer} role="note" aria-label="Disclaimer">
      <div className={styles.disclaimerIcon} aria-hidden="true">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>
      <div className={styles.disclaimerBody}>
        <p className={styles.disclaimerTitle}>{title}</p>
        <p className={styles.disclaimerText}>{content}</p>
      </div>
    </aside>
  );
}
