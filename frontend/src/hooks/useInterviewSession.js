'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { createRealtimeSession } from '@/lib/interviewRealtime';
import {
  createRealtimeClientSecret,
  ingestRealtimeEvent,
} from '@/services/interviewRealtimeApi';

const INITIAL_STATE = {
  status: 'idle',
  isAISpeaking: false,
  isUserSpeaking: false,
  isProcessing: false,
  transcript: [],
  turns: [],
  error: null,
};

export function useInterviewSession(sessionId, { mediaStream, questionLimit = 5 } = {}) {
  const [sessionState, setSessionState] = useState(INITIAL_STATE);
  const [elapsedTime, setElapsedTime] = useState(0);
  const sessionRef = useRef(null);

  useEffect(() => {
    if (!sessionId || !mediaStream) return undefined;

    const session = createRealtimeSession({
      sessionId,
      mediaStream,
      questionLimit,
      createClientSecret: createRealtimeClientSecret,
      sendAuditEvent: (event) => ingestRealtimeEvent(sessionId, event),
    });
    sessionRef.current = session;

    const onStatus = (status) => setSessionState((state) => ({
      ...state,
      status,
      error: status === 'connected' ? null : state.error,
    }));
    const onTranscript = () => setSessionState((state) => ({
      ...state,
      transcript: session.getState().transcript,
    }));
    const onTurns = (turns) => setSessionState((state) => ({ ...state, turns }));
    const onAI = (isAISpeaking) => setSessionState((state) => ({ ...state, isAISpeaking }));
    const onUser = (isUserSpeaking) => setSessionState((state) => ({ ...state, isUserSpeaking }));
    const onProcessing = (isProcessing) => setSessionState((state) => ({ ...state, isProcessing }));
    const onError = (error) => setSessionState((state) => ({ ...state, error }));

    session
      .on('stateChange', onStatus)
      .on('transcript', onTranscript)
      .on('turnsChange', onTurns)
      .on('aiSpeaking', onAI)
      .on('userSpeaking', onUser)
      .on('processing', onProcessing)
      .on('error', onError);

    setSessionState(INITIAL_STATE);
    return () => {
      sessionRef.current = null;
      void session.destroy();
    };
  }, [sessionId, mediaStream, questionLimit]);

  useEffect(() => {
    if (sessionState.status !== 'connected') return undefined;
    const timer = setInterval(() => setElapsedTime((value) => value + 1), 1000);
    return () => clearInterval(timer);
  }, [sessionState.status]);

  const connect = useCallback(async () => {
    setSessionState((state) => ({ ...state, error: null }));
    return sessionRef.current?.connect();
  }, []);

  const disconnect = useCallback((reason) => sessionRef.current?.disconnect(reason), []);
  const reconnect = useCallback(async () => {
    setSessionState((state) => ({ ...state, error: null }));
    return sessionRef.current?.reconnect();
  }, []);
  const cancelReconnect = useCallback(
    () => sessionRef.current?.cancelReconnect(),
    []
  );
  const retryPendingEvent = useCallback(
    () => sessionRef.current?.retryPendingEvent(),
    []
  );

  return {
    ...sessionState,
    elapsedTime,
    connect,
    disconnect,
    reconnect,
    cancelReconnect,
    retryPendingEvent,
  };
}
