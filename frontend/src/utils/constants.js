export const API_BASE_URL =
  typeof window !== 'undefined' && process.env.NEXT_PUBLIC_API_BASE_URL
    ? process.env.NEXT_PUBLIC_API_BASE_URL
    : 'http://localhost:8000';

// Google Sign-In web client ID. Empty when unconfigured — the UI then hides the
// Google button and falls back to email/password only. Never a secret.
export const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || '';

export const COLORS = {
  primary: '#2563EB',
  secondary: '#60A5FA',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  background: '#F8FAFC',
  card: '#FFFFFF',
};

export const STRICTNESS_OPTIONS = [
  { value: 'lenient', label: 'Dễ tính', description: 'Phân tích nới lỏng' },
  { value: 'balanced', label: 'Cân bằng', description: 'Đánh giá tiêu chuẩn' },
  { value: 'strict', label: 'Khắt khe', description: 'Đánh giá nghiêm ngặt' },
];

export const LANGUAGE_OPTIONS = [
  { value: 'vi', label: 'Tiếng Việt' },
  { value: 'en', label: 'Tiếng Anh' },
  { value: 'id', label: 'Tiếng Indonesia' },
  { value: 'es', label: 'Tiếng Tây Ban Nha' },
  { value: 'fr', label: 'Tiếng Pháp' },
  { value: 'de', label: 'Tiếng Đức' },
  { value: 'zh', label: 'Tiếng Trung' },
  { value: 'ja', label: 'Tiếng Nhật' },
];

export const ACCEPTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
};

export const ACCEPTED_EXTENSIONS = ['.pdf', '.docx'];

export const JOB_STATUS = {
  QUEUED: 'queued',
  RUNNING: 'running',
  SUCCEEDED: 'succeeded',
  FAILED: 'failed',
};

export const POLL_INTERVAL_MS = 2000;

export const MAX_JD_CHARACTERS = 5000;

export const WORKFLOW_STEPS = {
  IDLE: 'idle',
  UPLOADING: 'uploading',
  CREATING_JOB: 'creating_job',
  POLLING: 'polling',
  RESULT: 'result',
  ERROR: 'error',
};
