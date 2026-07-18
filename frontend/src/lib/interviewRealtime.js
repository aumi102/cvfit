/**
 * Interview Realtime Client — Mock WebRTC Session (Phase 8)
 *
 * Simulates a real-time AI interview session with event-driven state
 * management. When the backend WebRTC/WebSocket endpoint is ready,
 * replace the mock timers with actual signalling logic.
 *
 * Usage:
 *   const session = createRealtimeSession({ sessionId, questions });
 *   session.on('stateChange', (status) => { ... });
 *   session.on('transcript', (entry) => { ... });
 *   session.on('questionChange', (index) => { ... });
 *   session.on('aiSpeaking', (isSpeaking) => { ... });
 *   session.connect();
 */

import { CONNECTION_STATUS, MOCK_QUESTIONS } from './interviewTypes';

/**
 * Create a new realtime interview session controller.
 *
 * @param {{
 *   sessionId: string,
 *   questions?: Array<{ id: string, text: string, type?: string }>,
 *   autoAdvanceDelay?: number,
 * }} config
 * @returns {RealtimeSession}
 */
export function createRealtimeSession(config = {}) {
  const {
    sessionId = 'mock-session',
    questions = MOCK_QUESTIONS,
    autoAdvanceDelay = 12000,
  } = config;

  /* ─── Internal State ─── */
  let status = CONNECTION_STATUS.IDLE;
  let currentQuestionIndex = 0;
  let isAISpeaking = false;
  let isUserSpeaking = false;
  let transcript = [];
  let timers = [];
  let transcriptIdCounter = 0;

  /* ─── Event Listeners ─── */
  const listeners = {
    stateChange: [],
    transcript: [],
    questionChange: [],
    aiSpeaking: [],
    userSpeaking: [],
    error: [],
  };

  function emit(event, data) {
    (listeners[event] || []).forEach((fn) => {
      try { fn(data); } catch (e) { console.error(`[RealtimeSession] listener error:`, e); }
    });
  }

  function setStatus(newStatus) {
    status = newStatus;
    emit('stateChange', status);
  }

  function setAISpeaking(speaking) {
    isAISpeaking = speaking;
    emit('aiSpeaking', speaking);
  }

  function addTranscript(speaker, text) {
    const entry = {
      id: `t-${++transcriptIdCounter}`,
      speaker,
      text,
      timestamp: Date.now(),
    };
    transcript.push(entry);
    emit('transcript', entry);
    return entry;
  }

  function scheduleTimer(fn, delay) {
    const id = setTimeout(fn, delay);
    timers.push(id);
    return id;
  }

  function clearAllTimers() {
    timers.forEach(clearTimeout);
    timers = [];
  }

  /* ─── Mock AI Flow ─── */
  function startMockAIFlow() {
    // AI greets
    setAISpeaking(true);
    addTranscript('ai', 'Xin chào! Tôi là AI phỏng vấn viên của bạn. Chúng ta sẽ bắt đầu buổi phỏng vấn ngay bây giờ.');

    scheduleTimer(() => {
      setAISpeaking(false);
      askCurrentQuestion();
    }, 3000);
  }

  function askCurrentQuestion() {
    if (currentQuestionIndex >= questions.length) {
      endMockInterview();
      return;
    }

    const q = questions[currentQuestionIndex];
    emit('questionChange', currentQuestionIndex);

    scheduleTimer(() => {
      setAISpeaking(true);
      addTranscript('ai', q.text);

      scheduleTimer(() => {
        setAISpeaking(false);
        // Wait for user answer (auto-advance after delay in mock mode)
        scheduleTimer(() => {
          simulateUserAnswer();
        }, autoAdvanceDelay);
      }, 2500);
    }, 1000);
  }

  function simulateUserAnswer() {
    // In mock mode, simulate a user answering
    isUserSpeaking = true;
    emit('userSpeaking', true);

    scheduleTimer(() => {
      isUserSpeaking = false;
      emit('userSpeaking', false);
      addTranscript('user', '(Đang trả lời câu hỏi...)');

      // Move to next question
      currentQuestionIndex++;
      scheduleTimer(() => {
        askCurrentQuestion();
      }, 2000);
    }, 4000);
  }

  function endMockInterview() {
    setAISpeaking(true);
    addTranscript('ai', 'Cảm ơn bạn đã hoàn thành buổi phỏng vấn! Tôi sẽ tổng hợp kết quả ngay bây giờ.');

    scheduleTimer(() => {
      setAISpeaking(false);
      setStatus(CONNECTION_STATUS.DISCONNECTED);
    }, 3000);
  }

  /* ─── Public API ─── */
  const session = {
    /** Register an event listener. */
    on(event, fn) {
      if (listeners[event]) {
        listeners[event].push(fn);
      }
      return session;
    },

    /** Remove an event listener. */
    off(event, fn) {
      if (listeners[event]) {
        listeners[event] = listeners[event].filter((f) => f !== fn);
      }
      return session;
    },

    /** Connect to the AI interviewer (mock: simulates connection delay). */
    connect() {
      if (status === CONNECTION_STATUS.CONNECTED || status === CONNECTION_STATUS.CONNECTING) return;

      setStatus(CONNECTION_STATUS.CONNECTING);
      currentQuestionIndex = 0;
      transcript = [];

      scheduleTimer(() => {
        setStatus(CONNECTION_STATUS.CONNECTED);
        startMockAIFlow();
      }, 2000);
    },

    /** Disconnect from the session. */
    disconnect() {
      clearAllTimers();
      setAISpeaking(false);
      isUserSpeaking = false;
      emit('userSpeaking', false);
      setStatus(CONNECTION_STATUS.DISCONNECTED);
    },

    /** Reconnect after a drop. */
    reconnect() {
      clearAllTimers();
      setStatus(CONNECTION_STATUS.RECONNECTING);

      scheduleTimer(() => {
        setStatus(CONNECTION_STATUS.CONNECTED);
        addTranscript('ai', 'Kết nối đã được khôi phục. Chúng ta tiếp tục nhé.');
        scheduleTimer(() => {
          askCurrentQuestion();
        }, 2000);
      }, 3000);
    },

    /** Skip to next question. */
    skipQuestion() {
      clearAllTimers();
      setAISpeaking(false);
      isUserSpeaking = false;
      emit('userSpeaking', false);
      currentQuestionIndex++;
      askCurrentQuestion();
    },

    /** Manually advance user speaking state (for real mic integration). */
    setUserSpeaking(speaking) {
      isUserSpeaking = speaking;
      emit('userSpeaking', speaking);
    },

    /** Get current state snapshot. */
    getState() {
      return {
        status,
        currentQuestionIndex,
        totalQuestions: questions.length,
        currentQuestion: questions[currentQuestionIndex] || null,
        isAISpeaking,
        isUserSpeaking,
        transcript: [...transcript],
      };
    },

    /** Clean up all resources. */
    destroy() {
      clearAllTimers();
      Object.keys(listeners).forEach((key) => { listeners[key] = []; });
    },
  };

  return session;
}
