'use client';

import { useState, useMemo } from 'react';
import { useLanguage } from '@/context/LanguageContext';
import styles from '@/styles/InterviewPrep.module.css';

const TYPE_ORDER = ['technical', 'project_deep_dive', 'behavioral', 'gap_probe', 'system_design', 'situational', 'general'];

/**
 * InterviewPrep — Phase 4 Interview Prep Pack
 *
 * Accepts a plain array of question objects via the `questions` prop.
 * Backward-compatible: also accepts `{ interviewPrep }` where
 * interviewPrep is either a plain array or `{ questions: [...] }`.
 */
export default function InterviewPrep({ questions: questionsProp, interviewPrep }) {
  const { t } = useLanguage();
  const [expandedQuestions, setExpandedQuestions] = useState(new Set());

  // Normalize: prefer direct `questions` prop; fall back to interviewPrep shapes.
  const questions = useMemo(() => {
    if (Array.isArray(questionsProp) && questionsProp.length > 0) return questionsProp;
    if (Array.isArray(interviewPrep)) return interviewPrep;
    if (Array.isArray(interviewPrep?.questions)) return interviewPrep.questions;
    return [];
  }, [questionsProp, interviewPrep]);

  const grouped = useMemo(() => {
    const groups = new Map();
    for (const q of questions) {
      const type = (q.type ?? 'general').toLowerCase();
      if (!groups.has(type)) groups.set(type, []);
      groups.get(type).push(q);
    }
    const sorted = new Map();
    for (const type of TYPE_ORDER) {
      if (groups.has(type)) sorted.set(type, groups.get(type));
    }
    for (const [type, items] of groups) {
      if (!sorted.has(type)) sorted.set(type, items);
    }
    return sorted;
  }, [questions]);

  if (questions.length === 0) {
    return (
      <div className={styles.emptyState}>
        {t('phase4.interviewPrep.empty')}
      </div>
    );
  }

  const toggleQuestion = (id) => {
    setExpandedQuestions((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const typeIconClass = (type) => {
    const map = {
      behavioral: styles.typeIconBehavioral,
      technical: styles.typeIconTechnical,
      project_deep_dive: styles.typeIconTechnical,
      gap_probe: styles.typeIconSituational,
      system_design: styles.typeIconTechnical,
      situational: styles.typeIconSituational,
      general: styles.typeIconGeneral,
    };
    return map[type] || styles.typeIconGeneral;
  };

  const typeBadgeClass = (type) => {
    const map = {
      behavioral: styles.typeBehavioral,
      technical: styles.typeTechnical,
      project_deep_dive: styles.typeTechnical,
      gap_probe: styles.typeSituational,
      system_design: styles.typeTechnical,
      situational: styles.typeSituational,
      general: styles.typeGeneral,
    };
    return map[type] || styles.typeGeneral;
  };

  let globalIndex = 0;

  return (
    <div className={styles.prepContainer}>
      {Array.from(grouped.entries()).map(([type, items], gIndex) => (
        <div
          key={type}
          className={styles.typeGroup}
          style={{ animationDelay: `${gIndex * 0.08}s` }}
        >
          <div className={styles.typeGroupHeader}>
            <div className={`${styles.typeIcon} ${typeIconClass(type)}`} />
            <span className={styles.typeLabel}>
              {t(`phase4.interviewPrep.type.${type}`) || type}
            </span>
            <span className={styles.typeCount}>
              {items.length} {t('phase4.interviewPrep.questions')}
            </span>
          </div>

          {items.map((q, qIndex) => {
            globalIndex++;
            const qId = `q-${type}-${qIndex}`;
            const isOpen = expandedQuestions.has(qId);

            return (
              <div key={qId} className={styles.questionCard}>
                <div
                  className={styles.questionHeader}
                  onClick={() => toggleQuestion(qId)}
                  role="button"
                  tabIndex={0}
                  aria-expanded={isOpen}
                  onKeyDown={(e) => e.key === 'Enter' && toggleQuestion(qId)}
                >
                  <span className={styles.questionNumber}>{globalIndex}</span>
                  <span className={styles.questionText}>{q.question}</span>
                  <svg
                    className={`${styles.questionChevron} ${isOpen ? styles.questionChevronExpanded : ''}`}
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </div>

                {isOpen && (
                  <div className={styles.questionDetails}>
                    {q.why_this_question && (
                      <div className={styles.detailBlock}>
                        <span className={styles.detailLabel}>
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <circle cx="12" cy="12" r="10" />
                            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                            <line x1="12" y1="17" x2="12.01" y2="17" />
                          </svg>
                          {t('phase4.interviewPrep.whyThisQuestion')}
                        </span>
                        <p className={styles.detailValue}>{q.why_this_question}</p>
                      </div>
                    )}

                    {Array.isArray(q.suggested_answer_outline) && q.suggested_answer_outline.length > 0 && (
                      <div className={styles.detailBlock}>
                        <span className={styles.detailLabel}>
                          {t('phase4.interviewPrep.suggestedOutline')}
                        </span>
                        <ul className={styles.outlineBlock}>
                          {q.suggested_answer_outline.map((point, pIdx) => (
                            <li key={pIdx} className={styles.outlineItem}>{point}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {q.related_jd_requirement && (
                      <div className={styles.detailBlock}>
                        <span className={styles.detailLabel}>
                          {t('phase4.interviewPrep.relatedJd')}
                        </span>
                        <div className={styles.relatedBlock}>
                          {q.related_jd_requirement}
                        </div>
                      </div>
                    )}

                    {Array.isArray(q.related_cv_evidence) && q.related_cv_evidence.length > 0 && (
                      <div className={styles.detailBlock}>
                        <span className={styles.detailLabel}>
                          {t('phase4.interviewPrep.relatedCv')}
                        </span>
                        <div className={styles.relatedBlock}>
                          {q.related_cv_evidence.join(', ')}
                        </div>
                      </div>
                    )}

                    {q.risk_if_user_cannot_answer && (
                      <div className={styles.detailBlock}>
                        <span className={styles.detailLabel}>
                          {t('phase4.interviewPrep.risk')}
                        </span>
                        <div className={styles.riskBlock}>
                          {q.risk_if_user_cannot_answer}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}
