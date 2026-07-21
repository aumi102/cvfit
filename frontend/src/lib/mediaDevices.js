/**
 * Browser Media Device Helpers (Phase 8)
 *
 * Wraps the MediaDevices API with graceful error handling, permission
 * status checks, and an audio-level analyser for the microphone meter.
 *
 * All functions are safe to call on the server (they no-op/return defaults).
 */

/**
 * Request microphone access.
 * @returns {Promise<{ granted: boolean, stream: MediaStream|null, error: string|null }>}
 */
export async function requestMicrophonePermission() {
  if (typeof navigator === 'undefined' || !navigator.mediaDevices) {
    return { granted: false, stream: null, error: 'Trình duyệt không hỗ trợ truy cập microphone.' };
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    return { granted: true, stream, error: null };
  } catch (err) {
    return { granted: false, stream: null, error: mapMediaError(err, 'microphone') };
  }
}

/**
 * Request camera access.
 * @param {{ facingMode?: string }} opts
 * @returns {Promise<{ granted: boolean, stream: MediaStream|null, error: string|null }>}
 */
export async function requestCameraPermission(opts = {}) {
  if (typeof navigator === 'undefined' || !navigator.mediaDevices) {
    return { granted: false, stream: null, error: 'Trình duyệt không hỗ trợ truy cập camera.' };
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: opts.facingMode || 'user', width: { ideal: 640 }, height: { ideal: 480 } },
    });
    return { granted: true, stream, error: null };
  } catch (err) {
    return { granted: false, stream: null, error: mapMediaError(err, 'camera') };
  }
}

/**
 * Check the current permission status for a device kind.
 * Falls back to 'prompt' when the Permissions API is unavailable.
 * @param {'microphone'|'camera'} kind
 * @returns {Promise<'granted'|'denied'|'prompt'>}
 */
export async function checkPermissionStatus(kind) {
  if (typeof navigator === 'undefined' || !navigator.permissions) return 'prompt';
  try {
    const result = await navigator.permissions.query({ name: kind });
    return result.state; // 'granted' | 'denied' | 'prompt'
  } catch {
    return 'prompt';
  }
}

/**
 * Create an audio level analyser from a microphone stream.
 * Returns a function that, when called, returns the current volume (0-1).
 *
 * @param {MediaStream} stream
 * @returns {{ getLevel: () => number, cleanup: () => void }}
 */
export function createAudioAnalyser(stream) {
  if (!stream || typeof AudioContext === 'undefined') {
    return { getLevel: () => 0, cleanup: () => {} };
  }

  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const source = ctx.createMediaStreamSource(stream);
  const analyser = ctx.createAnalyser();
  analyser.fftSize = 256;
  analyser.smoothingTimeConstant = 0.8;
  source.connect(analyser);

  const dataArray = new Uint8Array(analyser.frequencyBinCount);

  function getLevel() {
    analyser.getByteFrequencyData(dataArray);
    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
      sum += dataArray[i];
    }
    return sum / (dataArray.length * 255);
  }

  function cleanup() {
    try { source.disconnect(); } catch { /* noop */ }
    try { ctx.close(); } catch { /* noop */ }
  }

  return { getLevel, cleanup };
}

/**
 * Stop all tracks on a media stream.
 * @param {MediaStream|null} stream
 */
export function stopStream(stream) {
  if (!stream) return;
  stream.getTracks().forEach((track) => track.stop());
}

/**
 * Map MediaDevices errors to user-friendly Vietnamese messages.
 * @param {Error} err
 * @param {'microphone'|'camera'} device
 * @returns {string}
 */
function mapMediaError(err, device) {
  const deviceName = device === 'microphone' ? 'microphone' : 'camera';
  switch (err.name) {
    case 'NotAllowedError':
    case 'PermissionDeniedError':
      return `Quyền truy cập ${deviceName} bị từ chối. Vui lòng cho phép trong cài đặt trình duyệt.`;
    case 'NotFoundError':
    case 'DevicesNotFoundError':
      return `Không tìm thấy ${deviceName}. Vui lòng kiểm tra thiết bị của bạn.`;
    case 'NotReadableError':
    case 'TrackStartError':
      return `${deviceName === 'microphone' ? 'Microphone' : 'Camera'} đang được sử dụng bởi ứng dụng khác.`;
    case 'OverconstrainedError':
      return `${deviceName === 'microphone' ? 'Microphone' : 'Camera'} không hỗ trợ cấu hình yêu cầu.`;
    case 'AbortError':
      return `Truy cập ${deviceName} bị hủy. Vui lòng thử lại.`;
    default:
      return `Không thể truy cập ${deviceName}: ${err.message || 'Lỗi không xác định'}`;
  }
}
