export class RealtimeEventConflictError extends Error {
  constructor(message = 'Chuỗi sự kiện phỏng vấn không còn đồng bộ.') {
    super(message);
    this.name = 'RealtimeEventConflictError';
  }
}

/**
 * Serializes CV Fit audit events. A failed request remains at the head of the
 * queue and is retried with the exact same sequence and payload.
 */
export function createRealtimeEventSequencer(sendEvent) {
  if (typeof sendEvent !== 'function') {
    throw new TypeError('sendEvent must be a function');
  }

  let nextSequence = 0;
  let pending = null;
  let chain = Promise.resolve();

  async function sendPending() {
    if (!pending) return null;
    const exactEvent = pending;
    const response = await sendEvent(exactEvent);
    pending = null;
    nextSequence += 1;
    return response;
  }

  async function deliver(eventType, payload = {}) {
    // A later event may trigger one retry, but it can never overtake the
    // failed event or receive a new sequence before the exact retry succeeds.
    if (pending) await sendPending();
    pending = Object.freeze({
      event_type: eventType,
      event_sequence: nextSequence,
      payload: Object.freeze({ ...payload }),
    });
    return sendPending();
  }

  return {
    enqueue(eventType, payload = {}) {
      const stablePayload = Object.freeze({ ...payload });
      const task = () => deliver(eventType, stablePayload);
      chain = chain.then(task, task);
      return chain;
    },
    retryPending() {
      if (!pending) return Promise.resolve(null);
      const task = () => sendPending();
      chain = chain.then(task, task);
      return chain;
    },
    getState() {
      return {
        nextSequence,
        pending: pending
          ? {
              event_type: pending.event_type,
              event_sequence: pending.event_sequence,
              payload: { ...pending.payload },
            }
          : null,
      };
    },
  };
}
