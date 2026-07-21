import apiClient from './apiClient';

const BASE_PATH = '/v1/interview/realtime/sessions';

export async function createRealtimeInterviewSession(payload = {}) {
  const response = await apiClient.post(BASE_PATH, {
    interview_type: payload.interview_type || 'mixed',
    difficulty: payload.difficulty || 'medium',
    question_limit: payload.question_limit || 5,
    mode: 'realtime_voice',
    consent_audio: payload.consent_audio === true,
    consent_camera: false,
    consent_recording: false,
    language: 'vi',
    ...(payload.target_job_id ? { target_job_id: payload.target_job_id } : {}),
    ...(payload.application_id ? { application_id: payload.application_id } : {}),
    ...(payload.analysis_job_id ? { analysis_job_id: payload.analysis_job_id } : {}),
  });
  return response.data;
}

export async function listRealtimeInterviewSessions(params = {}) {
  const response = await apiClient.get(BASE_PATH, { params });
  return response.data;
}

export async function getRealtimeInterviewSession(sessionId) {
  const response = await apiClient.get(`${BASE_PATH}/${sessionId}`);
  return response.data;
}

export async function createRealtimeClientSecret(sessionId) {
  const response = await apiClient.post(`${BASE_PATH}/${sessionId}/client-secret`);
  return response.data;
}

export async function ingestRealtimeEvent(sessionId, event) {
  const response = await apiClient.post(`${BASE_PATH}/${sessionId}/events`, event);
  return response.data;
}

export async function completeRealtimeInterviewSession(sessionId, payload) {
  const response = await apiClient.post(`${BASE_PATH}/${sessionId}/complete`, payload);
  return response.data;
}

export async function getRealtimeInterviewSummary(sessionId) {
  const response = await apiClient.get(`${BASE_PATH}/${sessionId}/summary`, {
    validateStatus: (status) => status === 200 || status === 202,
  });
  return response.data;
}
