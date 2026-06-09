'use client';

import { useLanguage } from '@/context/LanguageContext';
import styles from '@/styles/SafeRewrite.module.css';

/**
 * SafeRewrite — Phase 4 Safe Rewrite Suggestions
 *
 * Renders backend `safe_rewrite_suggestions` (v3 structured templates) when
 * available.  Falls back to improvement_actions[type==='cv_rewrite'] for
 * backward compatibility.
 *
 * Props:
 *   suggestions  — plain array from data.safe_rewrite_suggestions (preferred)
 *   actions      — improvement_actions array (fallback source)
 *   evidence     — evidence array for evidence lookups
 */
export default function SafeRewrite({ suggestions, actions, evidence }) {
  const { t } = useLanguage();

  // Use backend structured suggestions when available; otherwise fall back to
  // improvement_actions items whose type is 'cv_rewrite'.
  const useSuggestions = Array.isArray(suggestions) && suggestions.length > 0;
  const fallbackActions = useSuggestions
    ? []
    : (actions ?? []).filter((a) => a.type === 'cv_rewrite');

  const hasContent = useSuggestions || fallbackActions.length > 0;
  if (!hasContent) {
    return (
      <div className={styles.emptyState}>
        {t('phase4.safeRewrite.empty')}
      </div>
    );
  }

  // Evidence lookup for action-based fallback items.
  const evidenceMap = {};
  if (Array.isArray(evidence)) {
    for (const ev of evidence) {
      if (ev.id) evidenceMap[ev.id] = ev;
    }
  }

  return (
    <div className={styles.rewriteContainer}>
      {/* Prominent warning banner */}
      <div className={styles.warningBanner} id="safe-rewrite-warning">
        <svg className={styles.warningIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0-3.42 0z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
        <div className={styles.warningContent}>
          <span className={styles.warningTitle}>{t('phase4.safeRewrite.warning')}</span>
          <span className={styles.warningDetail}>{t('phase4.safeRewrite.warningDetail')}</span>
        </div>
      </div>

      {/* ── v3 structured suggestions ── */}
      {useSuggestions && suggestions.map((item, index) => (
        <div
          key={`suggestion-${index}`}
          className={styles.rewriteCard}
          style={{ animationDelay: `${index * 0.06}s` }}
        >
          {/* Suggested structure template */}
          {item.suggested_structure && (
            <div className={styles.suggestedRewrite}>
              <span className={styles.evidenceLabel}>
                {t('phase4.safeRewrite.suggestedRewrite')}
              </span>
              <div className={styles.suggestedText}>
                {item.suggested_structure}
              </div>
            </div>
          )}

          {/* Source evidence IDs */}
          {Array.isArray(item.source_evidence) && item.source_evidence.length > 0 && (
            <div className={styles.currentEvidence}>
              <span className={styles.evidenceLabel}>
                {t('phase4.safeRewrite.currentEvidence')}
              </span>
              <div className={styles.evidenceText}>
                {item.source_evidence.join(', ')}
              </div>
            </div>
          )}

          {/* What to confirm before using */}
          {Array.isArray(item.missing_context_to_confirm) && item.missing_context_to_confirm.length > 0 && (
            <div className={styles.currentEvidence}>
              <span className={styles.evidenceLabel}>
                {t('phase4.safeRewrite.confirmBefore')}
              </span>
              <ul className={styles.confirmList}>
                {item.missing_context_to_confirm.map((ctx, cIdx) => (
                  <li key={cIdx} className={styles.confirmItem}>{ctx}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Per-item warning */}
          {item.warning && (
            <div className={styles.guardrail}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
              {item.warning}
            </div>
          )}

          {/* do_not_fabricate guardrail */}
          {item.do_not_fabricate === true && (
            <div className={styles.guardrail}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
              {t('phase4.safeRewrite.doNotFabricate')}
            </div>
          )}
        </div>
      ))}

      {/* ── Fallback: improvement_actions[type=cv_rewrite] ── */}
      {!useSuggestions && fallbackActions.map((action, index) => {
        const linkedEvidence = (action.related_evidence_ids ?? [])
          .map((id) => evidenceMap[id])
          .filter(Boolean);
        const currentEvidenceText = linkedEvidence
          .map((ev) => ev.text)
          .filter(Boolean)
          .join(' • ') || null;

        return (
          <div
            key={action.id ?? `rewrite-${index}`}
            className={styles.rewriteCard}
            style={{ animationDelay: `${index * 0.06}s` }}
          >
            <div className={styles.rewriteHeader}>
              <span className={styles.rewriteTitle}>{action.title}</span>
            </div>

            {currentEvidenceText && (
              <div className={styles.currentEvidence}>
                <span className={styles.evidenceLabel}>
                  {t('phase4.safeRewrite.currentEvidence')}
                </span>
                <div className={styles.evidenceText}>
                  {currentEvidenceText}
                </div>
              </div>
            )}

            {action.suggestion && (
              <div className={styles.suggestedRewrite}>
                <span className={styles.evidenceLabel}>
                  {t('phase4.safeRewrite.suggestedRewrite')}
                </span>
                <div className={styles.suggestedText}>
                  {action.suggestion}
                </div>
              </div>
            )}

            {action.guardrail && (
              <div className={styles.guardrail}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
                {action.guardrail}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
