'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import { useMediaDevices } from '@/hooks/useMediaDevices';
import { useInterviewSession } from '@/hooks/useInterviewSession';
import {
  completeRealtimeInterviewSession,
  getRealtimeInterviewSession,
} from '@/services/interviewRealtimeApi';
import { CONNECTION_STATUS } from '@/lib/interviewTypes';
import styles from '@/styles/InterviewRoom.module.css';

import PageShell from '@/components/common/PageShell';
import LoadingOverlay from '@/components/interview-room/LoadingOverlay';
import InterviewSkeleton from '@/components/interview-room/InterviewSkeleton';
import PermissionDeniedFallback from '@/components/interview-room/PermissionDeniedFallback';
import MicrophoneMeter from '@/components/interview-room/MicrophoneMeter';
import RealtimeConnectionStatus from '@/components/interview-room/RealtimeConnectionStatus';
import AIInterviewerPanel from '@/components/interview-room/AIInterviewerPanel';
import TranscriptPanel from '@/components/interview-room/TranscriptPanel';
import QuestionProgress from '@/components/interview-room/QuestionProgress';
import AnswerTimer from '@/components/interview-room/AnswerTimer';

function featureMessage(error) {
  if (error?.response?.status === 503) {
    return 'Phỏng vấn bằng giọng nói hiện chưa được cấu hình.';
  }
  if (error?.response?.status === 404) {
    return 'Không tìm thấy phiên phỏng vấn hoặc bạn không có quyền truy cập.';
  }
  return 'Không thể tải thông tin phiên phỏng vấn.';
}

export default function InterviewRoomPage() {
  const { isAuthChecking } = useRequireAuth();
  const { id } = useParams();
  const router = useRouter();
  const [sessionData, setSessionData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [pageError, setPageError] = useState(null);
  const [startRequested, setStartRequested] = useState(false);
  const [isEnding, setIsEnding] = useState(false);
  const endingRef = useRef(false);

  const {
    micStatus,
    micStream,
    audioLevel,
    isMuted,
    toggleMute,
    requestMic,
    stopAll,
  } = useMediaDevices();

  const {
    status: connectionStatus,
    isAISpeaking,
    isUserSpeaking,
    isProcessing,
    transcript,
    turns,
    error: connectionError,
    elapsedTime,
    connect,
    disconnect,
    reconnect,
    cancelReconnect,
  } = useInterviewSession(id, {
    mediaStream: micStream,
    questionLimit: sessionData?.question_limit || 5,
  });

  useEffect(() => {
    if (isAuthChecking) return undefined;
    let active = true;
    setIsLoading(true);
    getRealtimeInterviewSession(id)
      .then((data) => {
        if (!active) return;
        setSessionData(data);
      })
      .catch((error) => {
        if (!active) return;
        setPageError(featureMessage(error));
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => {
      active = false;
    };
  }, [id, isAuthChecking]);

  useEffect(() => {
    if (!startRequested || !micStream || connectionStatus !== CONNECTION_STATUS.IDLE) {
      return;
    }
    void connect().catch(() => undefined);
  }, [startRequested, micStream, connectionStatus, connect]);

  const handleStart = useCallback(async () => {
    setPageError(null);
    setStartRequested(true);
    const permission = await requestMic();
    if (!permission.granted) {
      setPageError(permission.error || 'Không thể sử dụng microphone.');
    }
  }, [requestMic]);

  const handleEndSession = useCallback(async () => {
    if (endingRef.current) return;
    endingRef.current = true;
    setIsEnding(true);
    setPageError(null);
    try {
      await disconnect('user_ended');
      stopAll();
      await completeRealtimeInterviewSession(id, {
        completion_reason: 'user_ended',
        turns: turns.map((turn) => ({
          turn_index: turn.turn_index,
          question_text: turn.question_text,
          ...(turn.question_type ? { question_type: turn.question_type } : {}),
          ...(turn.answer_transcript ? { answer_transcript: turn.answer_transcript } : {}),
          ...(turn.ai_followup_text ? { ai_followup_text: turn.ai_followup_text } : {}),
          ...(turn.started_at ? { started_at: turn.started_at } : {}),
          ...(turn.ended_at ? { ended_at: turn.ended_at } : {}),
        })),
      });
      router.replace(`/interview/sessions/${id}/summary`);
    } catch {
      endingRef.current = false;
      setPageError('Không thể kết thúc phiên an toàn. Vui lòng thử lại.');
      setIsEnding(false);
    }
  }, [disconnect, id, router, stopAll, turns]);

  const currentQuestion = useMemo(() => {
    const turn = turns[turns.length - 1];
    return turn ? { id: turn.turn_index, text: turn.question_text } : null;
  }, [turns]);

  if (isAuthChecking || isLoading) {
    return (
      <PageShell isAuthChecking={isAuthChecking} maxWidth="100%">
        <InterviewSkeleton />
      </PageShell>
    );
  }

  if (micStatus === 'denied' && startRequested) {
    return (
      <PageShell isAuthChecking={false} maxWidth="100%">
        <PermissionDeniedFallback onRetry={handleStart} fallbackUrl={`/applications/${sessionData?.application_id || ''}/interview`} />
      </PageShell>
    );
  }

  const hasStarted = connectionStatus !== CONNECTION_STATUS.IDLE;
  const showLoadingOverlay = connectionStatus === CONNECTION_STATUS.CONNECTING;
  const visibleError = pageError || connectionError?.message;

  return (
    <PageShell isAuthChecking={false} maxWidth="1400px">
      {showLoadingOverlay && <LoadingOverlay />}

      <div className={styles.roomHeader}>
        <div className={styles.roomHeaderLeft}>
          <strong>Phỏng vấn bằng giọng nói</strong>
          <span className={styles.voiceLanguageBadge}>Tiếng Việt</span>
        </div>
        <div className={styles.roomHeaderRight}>
          <RealtimeConnectionStatus status={connectionStatus} />
          <AnswerTimer seconds={elapsedTime} />
        </div>
      </div>

      {visibleError && (
        <div className={styles.voiceError} role="alert">
          <span>{visibleError}</span>
          {connectionStatus === CONNECTION_STATUS.RECONNECTING ? (
            <button type="button" onClick={cancelReconnect}>
              Hủy kết nối lại
            </button>
          ) : connectionError?.retryable && micStream ? (
            <button type="button" onClick={() => void reconnect().catch(() => undefined)}>
              Kết nối lại
            </button>
          ) : null}
        </div>
      )}

      {!hasStarted && (
        <section className={styles.voiceStartCard} aria-labelledby="voice-start-title">
          <div className={styles.voiceStartIcon} aria-hidden="true">🎙️</div>
          <h1 id="voice-start-title">Phỏng vấn bằng giọng nói</h1>
          <p>
            AI sẽ đặt từng câu hỏi bằng tiếng Việt và lắng nghe câu trả lời qua microphone.
          </p>
          <ul>
            <li>Âm thanh được truyền trực tiếp bằng WebRTC.</li>
            <li>CVFit không ghi âm và không lưu dữ liệu audio hoặc SDP.</li>
            <li>Bạn có thể tắt microphone hoặc kết thúc phiên bất cứ lúc nào.</li>
          </ul>
          <button
            type="button"
            className={styles.btnPrimary}
            onClick={handleStart}
            disabled={Boolean(pageError && !sessionData) || startRequested}
            aria-label="Bắt đầu phỏng vấn bằng giọng nói và cho phép microphone"
          >
            {startRequested ? 'Đang chuẩn bị microphone…' : 'Bắt đầu phỏng vấn'}
          </button>
        </section>
      )}

      {hasStarted && (
        <div className={styles.voiceRoomContainer}>
          <div className={styles.voiceStatusPanel} aria-live="polite">
            <h2>Trạng thái phiên</h2>
            <MicrophoneMeter level={audioLevel} isMuted={isMuted} />
            <p>
              {isAISpeaking
                ? 'AI đang nói'
                : isUserSpeaking
                  ? 'Đang nghe bạn trả lời'
                  : isProcessing
                    ? 'Đang xử lý'
                    : connectionStatus === CONNECTION_STATUS.CONNECTED
                      ? 'Đã kết nối — sẵn sàng lắng nghe'
                      : 'Mất kết nối'}
            </p>
          </div>

          <div className={styles.voiceQuestionPanel}>
            <AIInterviewerPanel
              currentQuestion={currentQuestion}
              isAISpeaking={isAISpeaking}
              isUserSpeaking={isUserSpeaking}
            />
            <QuestionProgress currentIndex={Math.max(0, turns.length - 1)} total={sessionData?.question_limit || 5} />
          </div>

          <div className={styles.voiceTranscriptPanel}>
            <TranscriptPanel transcript={transcript} />
          </div>

          <div className={styles.voiceControlsBar}>
            <button
              type="button"
              className={styles.controlBtn}
              onClick={toggleMute}
              aria-label={isMuted ? 'Bật microphone' : 'Tắt microphone'}
            >
              {isMuted ? 'Bật microphone' : 'Tắt microphone'}
            </button>
            <button
              type="button"
              className={`${styles.controlBtn} ${styles['controlBtn--danger']}`}
              onClick={handleEndSession}
              disabled={isEnding}
            >
              {isEnding ? 'Đang kết thúc…' : 'Kết thúc phiên'}
            </button>
          </div>
        </div>
      )}
    </PageShell>
  );
}
