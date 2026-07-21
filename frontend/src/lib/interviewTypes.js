/**
 * Interview Room — Shared Constants, Enums & Mock Data (Phase 8)
 *
 * Central source of truth for interview-related constants used across
 * setup, room, and summary pages. Mock data enables full UI testing
 * without a live backend.
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

/* ─── Mock Questions ─── */
export const MOCK_QUESTIONS = [
  {
    id: 'mock-q1',
    text: 'Hãy giới thiệu về bản thân và kinh nghiệm làm việc của bạn.',
    type: 'behavioral',
  },
  {
    id: 'mock-q2',
    text: 'Bạn đã xử lý xung đột trong nhóm như thế nào? Cho một ví dụ cụ thể.',
    type: 'behavioral',
  },
  {
    id: 'mock-q3',
    text: 'Mô tả một dự án kỹ thuật phức tạp mà bạn đã hoàn thành. Bạn đã giải quyết những thách thức gì?',
    type: 'technical',
  },
  {
    id: 'mock-q4',
    text: 'Bạn đánh giá điểm mạnh và điểm yếu lớn nhất của mình là gì?',
    type: 'HR',
  },
  {
    id: 'mock-q5',
    text: 'Tại sao bạn muốn làm việc tại công ty chúng tôi? Bạn có thể đóng góp gì?',
    type: 'HR',
  },
];

/* ─── Mock Transcript ─── */
export const MOCK_TRANSCRIPT = [
  { id: 't1', speaker: 'ai', text: 'Xin chào! Tôi là AI phỏng vấn viên. Hôm nay chúng ta sẽ bắt đầu với một vài câu hỏi. Bạn đã sẵn sàng chưa?', timestamp: 0 },
  { id: 't2', speaker: 'user', text: 'Vâng, tôi đã sẵn sàng.', timestamp: 5 },
  { id: 't3', speaker: 'ai', text: 'Tuyệt vời! Câu hỏi đầu tiên: Hãy giới thiệu về bản thân và kinh nghiệm làm việc của bạn.', timestamp: 8 },
];

/* ─── Mock Summary ─── */
export const MOCK_SUMMARY = {
  overall_score: 7.5,
  rubric: {
    relevance: 8,
    evidence: 7,
    clarity: 8,
    structure: 7,
    confidence: 7.5,
    risk: 3,
  },
  strengths: [
    'Câu trả lời có cấu trúc rõ ràng, sử dụng phương pháp STAR hiệu quả',
    'Đưa ra được nhiều ví dụ cụ thể từ kinh nghiệm thực tế',
    'Thể hiện sự tự tin và nhiệt huyết trong giao tiếp',
  ],
  weaknesses: [
    'Một số câu trả lời hơi dài, cần tập trung vào điểm chính',
    'Chưa đề cập đủ về kết quả đo lường được (metrics)',
    'Cần cải thiện kỹ năng xử lý câu hỏi áp lực',
  ],
  questions: [
    {
      id: 'sq1',
      text: 'Hãy giới thiệu về bản thân và kinh nghiệm làm việc của bạn.',
      answer: 'Tôi có 5 năm kinh nghiệm trong phát triển phần mềm, chuyên về React và Node.js...',
      score: 8,
      feedback: 'Câu trả lời tốt, rõ ràng và có cấu trúc. Nên bổ sung thêm số liệu cụ thể.',
      rubric: { relevance: 8, evidence: 7, clarity: 9, structure: 8, confidence: 8, risk: 2 },
    },
    {
      id: 'sq2',
      text: 'Bạn đã xử lý xung đột trong nhóm như thế nào?',
      answer: 'Trong dự án gần đây, tôi đã gặp tình huống bất đồng ý kiến về kiến trúc hệ thống...',
      score: 7,
      feedback: 'Ví dụ cụ thể tốt, nhưng cần nhấn mạnh hơn kết quả đạt được.',
      rubric: { relevance: 7, evidence: 7, clarity: 7, structure: 7, confidence: 7, risk: 3 },
    },
    {
      id: 'sq3',
      text: 'Mô tả một dự án kỹ thuật phức tạp mà bạn đã hoàn thành.',
      answer: 'Tôi đã dẫn dắt việc migrate hệ thống monolith sang microservices...',
      score: 7.5,
      feedback: 'Trình bày kỹ thuật tốt. Cần giải thích rõ hơn về impact đối với business.',
      rubric: { relevance: 8, evidence: 7, clarity: 7, structure: 7, confidence: 7.5, risk: 3 },
    },
  ],
  improvements: [
    'Luyện tập trả lời ngắn gọn hơn, tập trung vào 2-3 điểm chính',
    'Chuẩn bị sẵn các số liệu và metrics cho mỗi dự án',
    'Thực hành phương pháp STAR cho tất cả câu hỏi hành vi',
    'Nghiên cứu kỹ về công ty và vị trí trước khi phỏng vấn',
  ],
  learning_tasks: [
    { title: 'Phương pháp STAR nâng cao', type: 'course', priority: 'high' },
    { title: 'Kỹ năng giao tiếp trong phỏng vấn', type: 'practice', priority: 'medium' },
    { title: 'Chuẩn bị câu hỏi kỹ thuật System Design', type: 'study', priority: 'high' },
  ],
  next_questions: [
    'Bạn xử lý deadline gấp như thế nào?',
    'Hãy mô tả cách bạn học một công nghệ mới.',
    'Bạn đã từng thất bại trong công việc chưa? Bạn đã rút ra bài học gì?',
  ],
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
