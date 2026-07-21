'use client';

import { Suspense, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import PageShell from '@/components/common/PageShell';
import InterviewSetupForm from '@/components/interview-room/InterviewSetupForm';
import { createRealtimeInterviewSession } from '@/services/interviewRealtimeApi';
import styles from '@/styles/InterviewRoom.module.css';

function createErrorMessage(error) {
  if (error?.response?.status === 503) {
    return 'Phỏng vấn bằng giọng nói hiện chưa được cấu hình.';
  }
  if (error?.response?.status === 422) {
    return 'Cấu hình phiên chưa hợp lệ. Vui lòng kiểm tra lại lựa chọn.';
  }
  return 'Không thể tạo phiên phỏng vấn bằng giọng nói. Vui lòng thử lại.';
}

function NewSessionContent() {
  const { isAuthChecking } = useRequireAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleCreate = async (setup) => {
    setIsSubmitting(true);
    setError(null);
    try {
      const applicationId = searchParams.get('application_id') || setup.application_id;
      const session = await createRealtimeInterviewSession({
        interview_type:
          setup.question_type === 'project' ? 'project_deep_dive' :
          setup.question_type === 'HR' ? 'hr' : setup.question_type,
        difficulty: setup.difficulty,
        question_limit: setup.question_count,
        target_job_id: setup.target_job_id || undefined,
        application_id: applicationId || undefined,
        consent_audio: setup.consent_audio,
      });
      router.push(`/interview/sessions/${session.id}/room`);
    } catch (cause) {
      setError(createErrorMessage(cause));
      setIsSubmitting(false);
    }
  };

  return (
    <PageShell isAuthChecking={isAuthChecking} maxWidth="800px">
      <div className={styles.voiceModeIntro}>
        <span>Phỏng vấn bằng giọng nói</span>
        <p>Phiên mới mặc định sử dụng tiếng Việt.</p>
      </div>
      {error && <div className={styles.voiceError} role="alert">{error}</div>}
      <InterviewSetupForm
        initialData={{ application_id: searchParams.get('application_id') || '' }}
        onNext={handleCreate}
        onCancel={() => router.back()}
      />
      {isSubmitting && <p aria-live="polite">Đang tạo phiên an toàn…</p>}
    </PageShell>
  );
}

export default function NewSessionPage() {
  return (
    <Suspense fallback={<p>Đang tải cấu hình phỏng vấn…</p>}>
      <NewSessionContent />
    </Suspense>
  );
}
