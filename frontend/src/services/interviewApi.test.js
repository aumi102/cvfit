import { beforeEach, describe, expect, it, vi } from 'vitest';

const apiClient = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}));

vi.mock('./apiClient', () => ({ default: apiClient }));

import { getInterviewQuestions, submitAnswer } from './interviewApi';

describe('Vietnamese text interview API contract', () => {
  beforeEach(() => {
    apiClient.get.mockReset().mockResolvedValue({ data: { questions: [] } });
    apiClient.post.mockReset().mockResolvedValue({ data: {} });
  });

  it('requests newly generated questions in Vietnamese', async () => {
    await getInterviewQuestions('app-1');
    expect(apiClient.get).toHaveBeenCalledWith(
      '/v1/applications/app-1/interview/questions',
      { params: { language: 'vi' } }
    );
  });

  it('submits answer evaluation with the Vietnamese language contract', async () => {
    await submitAnswer('app-1', {
      question_id: 'q-1',
      question: 'Hãy mô tả dự án.',
      answer_text: 'Tôi đã xây dựng API.',
    });
    expect(apiClient.post).toHaveBeenCalledWith(
      '/v1/applications/app-1/interview/answers',
      expect.objectContaining({ language: 'vi' })
    );
  });
});
