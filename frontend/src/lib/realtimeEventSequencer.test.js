import { describe, expect, it, vi } from 'vitest';
import { createRealtimeEventSequencer } from './realtimeEventSequencer';

describe('createRealtimeEventSequencer', () => {
  it('starts at zero and advances without gaps', async () => {
    const send = vi.fn().mockResolvedValue({ accepted: true });
    const sequencer = createRealtimeEventSequencer(send);

    await sequencer.enqueue('session_connected', { transport: 'webrtc' });
    await sequencer.enqueue('question_started', { turn_index: 0, question_text: 'Xin chào' });

    expect(send.mock.calls.map(([event]) => event.event_sequence)).toEqual([0, 1]);
    expect(sequencer.getState()).toEqual({ nextSequence: 2, pending: null });
  });

  it('retries the exact object, payload and sequence after a network failure', async () => {
    const send = vi.fn()
      .mockRejectedValueOnce(new Error('network'))
      .mockResolvedValueOnce({ accepted: true });
    const sequencer = createRealtimeEventSequencer(send);

    await expect(
      sequencer.enqueue('user_transcript_completed', { turn_index: 0, transcript: 'Tôi đã trả lời.' })
    ).rejects.toThrow('network');
    expect(sequencer.getState().pending.event_sequence).toBe(0);

    await sequencer.retryPending();

    expect(send).toHaveBeenCalledTimes(2);
    expect(send.mock.calls[1][0]).toBe(send.mock.calls[0][0]);
    expect(sequencer.getState()).toEqual({ nextSequence: 1, pending: null });
  });

  it('never lets a queued event overtake a failed event', async () => {
    const send = vi.fn()
      .mockRejectedValueOnce(new Error('temporary'))
      .mockResolvedValue({ accepted: true });
    const sequencer = createRealtimeEventSequencer(send);

    await expect(sequencer.enqueue('question_started', { turn_index: 0 })).rejects.toThrow();
    await sequencer.enqueue('question_completed', { turn_index: 0 });

    expect(send.mock.calls.map(([event]) => event.event_sequence)).toEqual([0, 0, 1]);
    expect(send.mock.calls[1][0]).toBe(send.mock.calls[0][0]);
  });
});
