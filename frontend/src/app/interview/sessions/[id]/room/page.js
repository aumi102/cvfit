'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import { useMediaDevices } from '@/hooks/useMediaDevices';
import { useInterviewSession } from '@/hooks/useInterviewSession';
import { getSession, generateSessionQuestions, endSession } from '@/services/interviewSessionsApi';
import { trackEvent, ANALYTICS_EVENTS } from '@/lib/analytics';
import { CONNECTION_STATUS } from '@/lib/interviewTypes';
import styles from '@/styles/InterviewRoom.module.css';

// Components
import PageShell from '@/components/common/PageShell';
import LoadingOverlay from '@/components/interview-room/LoadingOverlay';
import InterviewSkeleton from '@/components/interview-room/InterviewSkeleton';
import InterviewErrorBanner from '@/components/interview-room/InterviewErrorBanner';
import PermissionDeniedFallback from '@/components/interview-room/PermissionDeniedFallback';
import CameraPreview from '@/components/interview-room/CameraPreview';
import MicrophoneMeter from '@/components/interview-room/MicrophoneMeter';
import RealtimeConnectionStatus from '@/components/interview-room/RealtimeConnectionStatus';
import AIInterviewerPanel from '@/components/interview-room/AIInterviewerPanel';
import TranscriptPanel from '@/components/interview-room/TranscriptPanel';
import QuestionProgress from '@/components/interview-room/QuestionProgress';
import AnswerTimer from '@/components/interview-room/AnswerTimer';
import SessionControls from '@/components/interview-room/SessionControls';

export default function InterviewRoomPage() {
  const { isAuthChecking } = useRequireAuth();
  const { id } = useParams();
  const router = useRouter();

  // Local state
  const [sessionData, setSessionData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [questionsGenerated, setQuestionsGenerated] = useState(false);

  // Hooks
  const { 
    micStatus, camStatus, micStream, camStream, audioLevel,
    isMuted, isCameraOff, toggleMute, toggleCamera, requestMic, requestCam, stopAll 
  } = useMediaDevices();

  const {
    status: connectionStatus, currentQuestionIndex, totalQuestions, currentQuestion,
    isAISpeaking, transcript, elapsedTime, connect, disconnect, setUserSpeaking
  } = useInterviewSession(id, { questions: sessionData?.questions || [] });

  // Load session data and request permissions
  useEffect(() => {
    if (isAuthChecking) return;
    let active = true;

    async function init() {
      try {
        // 1. Get session details
        let data = await getSession(id);
        
        // 2. Read config from session storage (if coming from setup wizard)
        let count = 5;
        try {
          const configStr = sessionStorage.getItem(`session_config_${id}`);
          if (configStr) {
            const config = JSON.parse(configStr);
            if (config.question_count) count = config.question_count;
          }
        } catch(e) {}

        // 3. Generate questions if new session
        if (!data.questions || data.questions.length === 0) {
          await generateSessionQuestions(id, {
            question_type: data.question_type,
            difficulty: data.difficulty,
            count: count,
          });
          data = await getSession(id);
        }
        
        if (!active) return;
        setSessionData(data);
        setQuestionsGenerated(true);

        // 4. Ensure we have mic permission
        if (micStatus === 'prompt') {
          await requestMic();
        }

      } catch (err) {
        if (!active) return;
        console.error(err);
        setError("Không thể tải thông tin phiên phỏng vấn.");
      } finally {
        if (active) setIsLoading(false);
      }
    }

    init();

    return () => { active = false; };
  }, [isAuthChecking, id, requestMic, micStatus]);

  // Auto connect when ready
  useEffect(() => {
    if (questionsGenerated && micStatus === 'granted' && connectionStatus === CONNECTION_STATUS.IDLE) {
      connect();
    }
  }, [questionsGenerated, micStatus, connectionStatus, connect]);

  // Voice activity detection (VAD) - mock integration
  // Automatically updates the AI panel's user speaking indicator based on audio level
  useEffect(() => {
    const isSpeaking = audioLevel > 0.05 && !isMuted;
    setUserSpeaking(isSpeaking);
  }, [audioLevel, isMuted, setUserSpeaking]);

  // Clean up streams on unmount
  useEffect(() => {
    return () => {
      stopAll();
      disconnect();
    };
  }, [stopAll, disconnect]);

  const handleEndSession = async () => {
    disconnect();
    stopAll();
    try {
      await endSession(id);
    } catch(e) {
      console.error("End session failed:", e);
    }
    router.replace(`/interview/sessions/${id}/summary`);
  };

  const handleRetryMic = async () => {
    setError(null);
    await requestMic();
  };

  if (isAuthChecking || isLoading) {
    return (
      <PageShell isAuthChecking={isAuthChecking} maxWidth="100%">
        <InterviewSkeleton />
      </PageShell>
    );
  }

  // Handle permission denied state
  if (micStatus === 'denied') {
    return (
      <PageShell isAuthChecking={false} maxWidth="100%">
        <PermissionDeniedFallback 
          onRetry={handleRetryMic} 
          fallbackUrl={`/interview/sessions/${id}`} 
        />
      </PageShell>
    );
  }

  const showLoadingOverlay = connectionStatus === CONNECTION_STATUS.CONNECTING || connectionStatus === CONNECTION_STATUS.IDLE;

  return (
    <PageShell isAuthChecking={false} maxWidth="1400px">
      {showLoadingOverlay && <LoadingOverlay />}
      
      {/* Top Header Bar */}
      <div className={styles.roomHeader} style={{ marginBottom: '1rem' }}>
        <div className={styles.roomHeaderLeft}>
          <span style={{ fontWeight: 700, fontSize: '1.1rem' }}>AI Interview Room</span>
          <span style={{ padding: '2px 8px', background: 'var(--color-bg-alt)', borderRadius: 'var(--radius-full)', fontSize: 'var(--font-size-xs)', color: 'var(--color-primary)', fontWeight: 600 }}>
            {sessionData?.question_type?.toUpperCase()}
          </span>
        </div>
        <div className={styles.roomHeaderRight}>
          <RealtimeConnectionStatus status={connectionStatus} />
          <AnswerTimer seconds={elapsedTime} />
        </div>
      </div>

      {error && <InterviewErrorBanner message={error} onRetry={() => setError(null)} />}

      <div className={styles.roomContainer}>
        {/* Left Column: Video & Audio */}
        <div className={styles.roomLeft}>
          <CameraPreview 
            stream={camStream} 
            isOff={isCameraOff} 
            isMuted={isMuted} 
          />
          <MicrophoneMeter 
            level={audioLevel} 
            isMuted={isMuted} 
          />
        </div>

        {/* Center Column: AI Interviewer & Question */}
        <div className={styles.roomCenter}>
          <AIInterviewerPanel 
            currentQuestion={currentQuestion}
            isAISpeaking={isAISpeaking}
            isUserSpeaking={audioLevel > 0.05 && !isMuted}
          />
          <QuestionProgress 
            currentIndex={currentQuestionIndex} 
            total={totalQuestions} 
          />
        </div>

        {/* Right Column: Transcript */}
        <div className={styles.roomRight}>
          <TranscriptPanel transcript={transcript} />
        </div>

        {/* Bottom Controls */}
        <div className={styles.roomControls}>
          <SessionControls 
            isMuted={isMuted}
            isCameraOff={isCameraOff}
            onToggleMute={toggleMute}
            onToggleCamera={toggleCamera}
            onEndSession={handleEndSession}
          />
        </div>
      </div>
    </PageShell>
  );
}
