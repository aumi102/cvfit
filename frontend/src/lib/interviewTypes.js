/**
 * Interview Room — Shared Constants and Enums (Phase 8)
 *
 * Central source of truth for interview-related constants used across
 * setup, room, and summary pages.
 */

/* ─── Interview Types ─── */
export const INTERVIEW_TYPES = [
  { value: 'technical', label: 'Kỹ thuật', icon: '💻', desc: 'Code, hệ thống, giải quyết vấn đề' },
  { value: 'behavioral', label: 'Hành vi', icon: '🤝', desc: 'Làm việc nhóm, lãnh đạo, kể chuyện STAR' },
  { value: 'project', label: 'Dự án chuyên sâu', icon: '📁', desc: 'Công việc cũ, thành tựu, mức độ ảnh hưởng' },
  { value: 'HR', label: 'Nhân sự', icon: '🌐', desc: 'Phù hợp văn hóa, lương, mục tiêu nghề nghiệp' },
  { value: 'mixed', label: 'Tổng hợp', icon: '🎯', desc: 'Kết hợp tất cả các loại câu hỏi' },
];

/* ─── Difficulty Levels ─── */
export const DIFFICULTIES = [
  { value: 'easy', label: 'Dễ', icon: '🟢', desc: 'Khởi động, câu hỏi cơ bản' },
  { value: 'medium', label: 'Trung bình', icon: '🟡', desc: 'Mức phỏng vấn tiêu chuẩn' },
  { value: 'hard', label: 'Khó', icon: '🔴', desc: 'Cao cấp / cạnh tranh' },
];

/* ─── Connection States ─── */
export const CONNECTION_STATUS = {
  IDLE: 'idle',
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  DISCONNECTED: 'disconnected',
  RECONNECTING: 'reconnecting',
  FAILED: 'failed',
};

/* ─── Permission States ─── */
export const PERMISSION_STATUS = {
  PROMPT: 'prompt',
  GRANTED: 'granted',
  DENIED: 'denied',
  ERROR: 'error',
};

/* ─── Interview Session Status ─── */
export const SESSION_STATUS = {
  SETUP: 'setup',
  PERMISSIONS: 'permissions',
  READY: 'ready',
  IN_PROGRESS: 'in_progress',
  PAUSED: 'paused',
  ENDED: 'ended',
};

/* ─── Rubric Keys ─── */
export const RUBRIC_KEYS = ['relevance', 'evidence', 'clarity', 'structure', 'confidence', 'risk'];

export const RUBRIC_LABELS = {
  relevance: 'Mức độ liên quan',
  evidence: 'Bằng chứng',
  clarity: 'Độ rõ ràng',
  structure: 'Cấu trúc',
  confidence: 'Sự tự tin',
  risk: 'Rủi ro',
};

export const RUBRIC_DESCS = {
  relevance: 'Mức độ trả lời trực tiếp vào câu hỏi',
  evidence: 'Các ví dụ và dẫn chứng cụ thể được sử dụng',
  clarity: 'Giao tiếp rõ ràng, dễ hiểu',
  structure: 'Luồng và cấu trúc logic (ví dụ: STAR)',
  confidence: 'Giọng điệu, sự quyết đoán và sức thuyết phục',
  risk: 'Các dấu hiệu cảnh báo hoặc mối lo ngại tiềm ẩn',
};

/**
 * Format seconds into MM:SS display string.
 * @param {number} seconds
 * @returns {string}
 */
export function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}
