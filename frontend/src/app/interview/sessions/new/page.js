'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import { useMediaDevices } from '@/hooks/useMediaDevices';
import PageShell from '@/components/common/PageShell';
import { createSession } from '@/services/interviewSessionsApi';
import { extractApiError } from '@/utils/errorHelpers';
import { trackEvent, ANALYTICS_EVENTS } from '@/lib/analytics';
import styles from '@/styles/InterviewRoom.module.css';

import InterviewSetupForm from '@/components/interview-room/InterviewSetupForm';
import DevicePermissionCheck from '@/components/interview-room/DevicePermissionCheck';

const STEPS = {
  SETUP: 0,
  PERMISSIONS: 1,
};

export default function NewSessionPage() {
  const { isAuthChecking } = useRequireAuth();
  const router = useRouter();
  const { micStatus, camStatus, requestMic, requestCam, stopAll } = useMediaDevices();

  const [currentStep, setCurrentStep] = useState(STEPS.SETUP);
  const [setupData, setSetupData] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSetupComplete = (data) => {
    setSetupData(data);
    setCurrentStep(STEPS.PERMISSIONS);
  };

  const handlePermissionsComplete = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      // 1. Create the session on the backend
      const session = await createSession({ 
        question_type: setupData.question_type, 
        difficulty: setupData.difficulty,
        target_job_id: setupData.target_job_id,
        application_id: setupData.application_id,
      });

      trackEvent(ANALYTICS_EVENTS.INTERVIEW_SESSION_CREATED, {
        feature_name: 'interview_sessions',
        question_type: setupData.question_type,
        difficulty: setupData.difficulty,
      });

      // 2. We need to pass the question_count to the room since it's used during question generation.
      // We'll store it in sessionStorage for the room page to pick up.
      if (typeof window !== 'undefined') {
        sessionStorage.setItem(`session_config_${session.id}`, JSON.stringify({
          question_count: setupData.question_count
        }));
      }

      // Stop local streams before navigating to the room (the room will request its own or reuse)
      stopAll();

      // 3. Navigate to the new interview room route
      router.push(`/interview/sessions/${session.id}/room`);
    } catch (err) {
      const { message } = extractApiError(err, 'Không thể bắt đầu phiên. Vui lòng thử lại.');
      setError(message);
      setIsSubmitting(false);
    }
  };

  return (
    <PageShell isAuthChecking={isAuthChecking} maxWidth="800px">
      <div style={{ paddingTop: '2rem' }}>
        {/* Wizard Steps Indicator */}
        <div className={styles.wizardSteps}>
          <div className={styles.wizardStep}>
            <div className={`${styles.wizardStepDot} ${currentStep === STEPS.SETUP ? styles['wizardStepDot--active'] : styles['wizardStepDot--done']}`}>
              {currentStep > STEPS.SETUP ? '✓' : '1'}
            </div>
            <span className={`${styles.wizardStepLabel} ${currentStep === STEPS.SETUP ? styles['wizardStepLabel--active'] : ''}`}>Cấu hình</span>
          </div>
          <div className={`${styles.wizardConnector} ${currentStep > STEPS.SETUP ? styles['wizardConnector--done'] : ''}`} />
          <div className={styles.wizardStep}>
            <div className={`${styles.wizardStepDot} ${currentStep === STEPS.PERMISSIONS ? styles['wizardStepDot--active'] : ''}`}>
              2
            </div>
            <span className={`${styles.wizardStepLabel} ${currentStep === STEPS.PERMISSIONS ? styles['wizardStepLabel--active'] : ''}`}>Thiết bị</span>
          </div>
        </div>

        {error && (
          <div style={{ marginBottom: '1rem' }}>
            <div className={styles.interviewError}>
              <div className={styles.interviewErrorText}>{error}</div>
            </div>
          </div>
        )}

        {currentStep === STEPS.SETUP && (
          <InterviewSetupForm 
            initialData={setupData}
            onNext={handleSetupComplete}
            onCancel={() => router.push('/interview/sessions')}
          />
        )}

        {currentStep === STEPS.PERMISSIONS && (
          <DevicePermissionCheck
            micStatus={micStatus}
            camStatus={camStatus}
            onRequestMic={requestMic}
            onRequestCam={requestCam}
            onNext={handlePermissionsComplete}
            onCancel={() => setCurrentStep(STEPS.SETUP)}
          />
        )}

        {isSubmitting && (
          <div style={{ textAlign: 'center', marginTop: '1rem', color: 'var(--color-text-muted)' }}>
            Đang khởi tạo phòng phỏng vấn...
          </div>
        )}
      </div>
    </PageShell>
  );
}
