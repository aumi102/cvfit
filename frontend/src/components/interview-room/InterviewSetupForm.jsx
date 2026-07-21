'use client';

import { useState, useEffect } from 'react';
import styles from '@/styles/InterviewRoom.module.css';
import { INTERVIEW_TYPES, DIFFICULTIES } from '@/lib/interviewTypes';
import { listTargetJobs } from '@/services/targetJobsApi';
import { listApplications } from '@/services/applicationsApi';
import ErrorBanner from '@/components/common/ErrorBanner';

export default function InterviewSetupForm({ initialData = {}, onNext, onCancel }) {
  const [formData, setFormData] = useState({
    question_type: initialData.question_type || 'mixed',
    difficulty: initialData.difficulty || 'medium',
    target_job_id: initialData.target_job_id || '',
    application_id: initialData.application_id || '',
    question_count: initialData.question_count || 5,
  });

  const [targetJobs, setTargetJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    setIsLoading(true);
    
    Promise.all([
      listTargetJobs().catch(() => ({ items: [] })),
      listApplications().catch(() => ({ items: [] }))
    ]).then(([jobsData, appsData]) => {
      if (!active) return;
      setTargetJobs(Array.isArray(jobsData?.items) ? jobsData.items : []);
      setApplications(Array.isArray(appsData?.items) ? appsData.items : []);
      setIsLoading(false);
    }).catch(err => {
      if (!active) return;
      console.error(err);
      setIsLoading(false);
    });

    return () => { active = false; };
  }, []);

  const handleChange = (key, value) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onNext(formData);
  };

  if (isLoading) {
    return (
      <div className={styles.formCard} style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
        <div className={styles.loadingDot} style={{ width: 12, height: 12, margin: '0 4px' }} />
        <div className={styles.loadingDot} style={{ width: 12, height: 12, margin: '0 4px', animationDelay: '0.2s' }} />
        <div className={styles.loadingDot} style={{ width: 12, height: 12, margin: '0 4px', animationDelay: '0.4s' }} />
      </div>
    );
  }

  return (
    <div className={styles.formCard}>
      <h1 className={styles.formTitle}>Cấu hình phiên phỏng vấn</h1>
      <p className={styles.formSubtitle}>
        Chọn loại câu hỏi và độ khó để AI có thể chuẩn bị tốt nhất cho buổi phỏng vấn của bạn.
      </p>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      <form onSubmit={handleSubmit} id="interview-setup-form">
        {/* Context Selection */}
        <div className={styles.fieldGroup} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div>
            <label className={styles.fieldLabel}>Công việc mục tiêu (Tùy chọn)</label>
            <select 
              className={styles.selectField}
              value={formData.target_job_id}
              onChange={(e) => handleChange('target_job_id', e.target.value)}
            >
              <option value="">-- Không chọn --</option>
              {targetJobs.map(job => (
                <option key={job.id} value={job.id}>{job.job_title} tại {job.company}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={styles.fieldLabel}>Hồ sơ ứng tuyển (Tùy chọn)</label>
            <select 
              className={styles.selectField}
              value={formData.application_id}
              onChange={(e) => handleChange('application_id', e.target.value)}
            >
              <option value="">-- Không chọn --</option>
              {applications.map(app => (
                <option key={app.id} value={app.id}>{app.job_title} tại {app.company_name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Question Type */}
        <div className={styles.fieldGroup}>
          <label className={styles.fieldLabel}>Loại câu hỏi</label>
          <div className={styles.optionGrid}>
            {INTERVIEW_TYPES.map((qt) => (
              <button
                key={qt.value}
                type="button"
                className={`${styles.optionCard} ${formData.question_type === qt.value ? styles['optionCard--selected'] : ''}`}
                onClick={() => handleChange('question_type', qt.value)}
                id={`qtype-${qt.value}`}
              >
                <div className={styles.optionIcon}>{qt.icon}</div>
                <div className={styles.optionLabel}>{qt.label}</div>
                <div className={styles.optionDesc}>{qt.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Difficulty */}
        <div className={styles.fieldGroup}>
          <label className={styles.fieldLabel}>Độ khó</label>
          <div className={styles.optionGrid} style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
            {DIFFICULTIES.map((d) => (
              <button
                key={d.value}
                type="button"
                className={`${styles.optionCard} ${formData.difficulty === d.value ? styles['optionCard--selected'] : ''}`}
                onClick={() => handleChange('difficulty', d.value)}
                id={`difficulty-${d.value}`}
              >
                <div className={styles.optionIcon}>{d.icon}</div>
                <div className={styles.optionLabel}>{d.label}</div>
                <div className={styles.optionDesc}>{d.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Question Count Slider */}
        <div className={styles.fieldGroup}>
          <label className={styles.fieldLabel}>Số lượng câu hỏi</label>
          <div className={styles.rangeGroup}>
            <input 
              type="range" 
              className={styles.rangeInput}
              min="3" 
              max="15" 
              step="1"
              value={formData.question_count}
              onChange={(e) => handleChange('question_count', parseInt(e.target.value, 10))}
            />
            <div className={styles.rangeValue}>{formData.question_count}</div>
          </div>
          <p className={styles.toggleDesc} style={{ marginTop: '0.5rem' }}>
            Thời gian dự kiến: khoảng {formData.question_count * 3} phút.
          </p>
        </div>

        <div className={styles.formActions}>
          {onCancel && (
            <button type="button" className={styles.btnSecondary} onClick={onCancel}>
              Hủy
            </button>
          )}
          <button type="submit" className={styles.btnPrimary} id="next-step-btn">
            Tiếp tục
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: 4 }}>
              <path d="M5 12h14" />
              <path d="m12 5 7 7-7 7" />
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
}
