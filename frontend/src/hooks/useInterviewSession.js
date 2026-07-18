'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { createRealtimeSession } from '@/lib/interviewRealtime';

/**
 * useInterviewSession
 * Custom hook to manage the realtime WebRTC mock session.
 */
export function useInterviewSession(sessionId, config = {}) {
  const [sessionState, setSessionState] = useState({
    status: 'idle',
    currentQuestionIndex: 0,
    totalQuestions: 0,
    currentQuestion: null,
    isAISpeaking: false,
    isUserSpeaking: false,
    transcript: [],
  });
  
  const [elapsedTime, setElapsedTime] = useState(0);
  const sessionRef = useRef(null);
  const timerRef = useRef(null);

  // Initialize session
  useEffect(() => {
    if (!sessionId) return;
    
    // Create the session mock
    const session = createRealtimeSession({ 
      sessionId, 
      questions: config.questions,
      autoAdvanceDelay: 12000 // Mock wait time before next question
    });
    
    sessionRef.current = session;

    // Attach listeners to sync state
    session.on('stateChange', status => setSessionState(s => ({ ...s, status })));
    session.on('questionChange', index => setSessionState(s => ({ ...s, currentQuestionIndex: index, currentQuestion: config.questions?.[index] })));
    session.on('aiSpeaking', isSpeaking => setSessionState(s => ({ ...s, isAISpeaking: isSpeaking })));
    session.on('userSpeaking', isSpeaking => setSessionState(s => ({ ...s, isUserSpeaking: isSpeaking })));
    session.on('transcript', entry => setSessionState(s => ({ ...s, transcript: [...session.getState().transcript] })));
    
    // Update initial state
    setSessionState(s => ({ 
      ...s, 
      ...session.getState(), 
      totalQuestions: config.questions?.length || 0 
    }));

    return () => {
      session.destroy();
      sessionRef.current = null;
    };
  }, [sessionId, config.questions]);

  // Handle timer
  useEffect(() => {
    if (sessionState.status === 'connected') {
      timerRef.current = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [sessionState.status]);

  const connect = useCallback(() => {
    if (sessionRef.current) sessionRef.current.connect();
  }, []);

  const disconnect = useCallback(() => {
    if (sessionRef.current) sessionRef.current.disconnect();
  }, []);

  const reconnect = useCallback(() => {
    if (sessionRef.current) sessionRef.current.reconnect();
  }, []);
  
  const skipQuestion = useCallback(() => {
    if (sessionRef.current) sessionRef.current.skipQuestion();
  }, []);

  // Simulates sending audio to the mock session (would be handled by WebRTC in real life)
  const setUserSpeaking = useCallback((isSpeaking) => {
    if (sessionRef.current) sessionRef.current.setUserSpeaking(isSpeaking);
  }, []);

  return {
    ...sessionState,
    elapsedTime,
    connect,
    disconnect,
    reconnect,
    skipQuestion,
    setUserSpeaking
  };
}
