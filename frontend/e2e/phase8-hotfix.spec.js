import { expect, test } from '@playwright/test';

const CORS_HEADERS = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type',
  'access-control-allow-methods': 'GET,POST,OPTIONS',
  'content-type': 'application/json',
};

async function authenticate(page) {
  await page.addInitScript(() => {
    localStorage.setItem('auth_token', 'synthetic.header.signature');
    localStorage.setItem('user', JSON.stringify({
      id: 'user-1',
      email: 'synthetic@example.com',
      full_name: 'Synthetic User',
      is_active: true,
    }));
  });
}

async function mockBackend(page, responder) {
  await page.route('http://localhost:8000/**', async (route) => {
    const request = route.request();
    if (request.method() === 'OPTIONS') {
      await route.fulfill({ status: 204, headers: CORS_HEADERS, body: '' });
      return;
    }
    const url = new URL(request.url());
    if (url.pathname === '/v1/auth/me') {
      await route.fulfill({
        status: 200,
        headers: CORS_HEADERS,
        body: JSON.stringify({
          id: 'user-1', email: 'synthetic@example.com',
          full_name: 'Synthetic User', is_active: true,
        }),
      });
      return;
    }
    if (url.pathname === '/v1/admin/me') {
      await route.fulfill({
        status: 200,
        headers: CORS_HEADERS,
        body: JSON.stringify({ is_admin: true, email: 'synthetic@example.com' }),
      });
      return;
    }
    const response = await responder({ request, url });
    if (!response) {
      await route.fulfill({ status: 404, headers: CORS_HEADERS, body: JSON.stringify({ detail: 'mock not found' }) });
      return;
    }
    await route.fulfill({
      status: response.status || 200,
      headers: { ...CORS_HEADERS, ...(response.headers || {}) },
      body: typeof response.body === 'string' ? response.body : JSON.stringify(response.body),
    });
  });
}

function collectBrowserErrors(page) {
  const errors = [];
  page.on('pageerror', (error) => errors.push(`pageerror: ${error.message}`));
  page.on('console', (message) => {
    if (message.type() === 'error') {
      const location = message.location()?.url || 'unknown';
      errors.push(`console: ${message.text()} @ ${location}`);
    }
  });
  return errors;
}

test('History opens an existing analysis detail and actions remain clickable', async ({ page }) => {
  const browserErrors = collectBrowserErrors(page);
  await authenticate(page);
  await mockBackend(page, async ({ url }) => {
    if (url.pathname === '/v1/jobs/history') {
      return {
        body: {
          items: [{
            job_id: 'job-history-1', status: 'succeeded', progress: 100,
            overall_fit_score: 82, target_role: 'Backend Developer',
            has_report: false, created_at: '2026-07-20T08:00:00Z',
          }],
        },
      };
    }
    if (url.pathname === '/v1/jobs/job-history-1/result') {
      return {
        body: {
          overall_score: 82,
          matched_skills: ['FastAPI'],
          missing_skills: ['Kubernetes'],
          strengths: ['Có bằng chứng dự án.'],
          weaknesses: ['Thiếu Kubernetes.'],
          recommendations: ['Chuẩn bị ví dụ thực tế.'],
        },
      };
    }
    return null;
  });

  await page.goto('/history');
  await page.getByRole('link', { name: 'Xem kết quả' }).click();

  await expect(page).toHaveURL(/\/history\/job-history-1$/);
  await expect(page.getByRole('heading', { name: 'Kết quả phân tích CV' })).toBeVisible();
  await expect(page.locator('#result-card')).toBeVisible();
  await expect(page.locator('#download-report-button')).toBeEnabled();
  await expect(page.locator('#new-analysis-button')).toBeEnabled();
  await page.locator('#new-analysis-button').scrollIntoViewIfNeeded();
  const center = await page.locator('#new-analysis-button').boundingBox();
  expect(center).not.toBeNull();
  const topElementId = await page.evaluate(({ x, y }) => {
    const element = document.elementFromPoint(x, y);
    return element?.closest('button')?.id || element?.id || '';
  }, { x: center.x + center.width / 2, y: center.y + center.height / 2 });
  expect(topElementId).toBe('new-analysis-button');
  await page.locator('#new-analysis-button').click();
  await expect(page).toHaveURL(/\/dashboard$/);
  expect(browserErrors).toEqual([]);
});

test('Text interview defaults new questions and feedback to Vietnamese', async ({ page }) => {
  const browserErrors = collectBrowserErrors(page);
  await authenticate(page);
  await mockBackend(page, async ({ request, url }) => {
    if (url.pathname === '/v1/applications/app-1/interview/questions') {
      expect(url.searchParams.get('language')).toBe('vi');
      return {
        body: {
          application_id: 'app-1',
          questions: [{
            question_id: 'q-1',
            question: 'Hãy mô tả một dự án thử thách mà bạn đã thực hiện.',
            type: 'behavioral', related_jd_requirement: 'Backend',
            related_cv_evidence: [], why_this_question: 'Câu hỏi luyện tập tiếng Việt.',
          }],
          disclaimer: 'Đây chỉ là nội dung luyện tập.',
        },
      };
    }
    if (url.pathname === '/v1/applications/app-1/interview/answers' && request.method() === 'GET') {
      return { body: { application_id: 'app-1', answers: [], total: 0 } };
    }
    if (url.pathname === '/v1/applications/app-1/interview/answers' && request.method() === 'POST') {
      const payload = request.postDataJSON();
      expect(payload.language).toBe('vi');
      return {
        status: 201,
        body: {
          rubric: { overall: 4, relevance: 4, specificity: 4, evidence: 3, structure: 4, risk_gap: 1 },
          feedback: {
            strengths: ['Câu trả lời rõ ràng và có cấu trúc.'],
            missing_evidence: [], suggested_improvements: ['Bổ sung kết quả đo lường.'],
            sample_outline: ['Tình huống', 'Hành động', 'Kết quả'], risk_notes: [],
            disclaimer: 'Hãy xem lại trước khi dùng trong phỏng vấn thực tế.',
          },
        },
      };
    }
    return null;
  });

  await page.goto('/applications/app-1/interview');
  await expect(page.getByRole('tab', { name: 'Phỏng vấn bằng giọng nói' })).toHaveAttribute('aria-selected', 'true');
  await page.getByRole('tab', { name: 'Luyện tập bằng văn bản' }).click();
  await expect(page.getByText('Hãy mô tả một dự án thử thách mà bạn đã thực hiện.')).toBeVisible();
  await page.getByLabel('Câu trả lời cho câu hỏi 1').fill('Tôi đã xây dựng API và cải thiện độ trễ 30%.');
  await page.getByRole('button', { name: 'Nộp câu trả lời' }).click();
  await expect(page.getByText('Câu trả lời rõ ràng và có cấu trúc.')).toBeVisible();
  expect(browserErrors).toEqual([]);
});

test('Voice mock connects WebRTC, shows live transcript, completes and opens summary', async ({ page }) => {
  const browserErrors = collectBrowserErrors(page);
  await authenticate(page);
  await page.addInitScript(() => {
    const track = { enabled: true, stop() {} };
    const stream = {
      getAudioTracks: () => [track],
      getTracks: () => [track],
    };
    Object.defineProperty(navigator, 'mediaDevices', {
      configurable: true,
      value: {
        getUserMedia: async (constraints) => {
          window.__micConstraints = constraints;
          return stream;
        },
      },
    });
    Object.defineProperty(navigator, 'permissions', {
      configurable: true,
      value: { query: async () => ({ state: 'prompt' }) },
    });
    class MockAudioContext {
      createMediaStreamSource() {
        return { connect() {}, disconnect() {} };
      }
      createAnalyser() {
        return {
          fftSize: 256,
          smoothingTimeConstant: 0.8,
          frequencyBinCount: 128,
          getByteFrequencyData(values) { values.fill(0); },
        };
      }
      close() {}
    }
    window.AudioContext = MockAudioContext;
    window.webkitAudioContext = MockAudioContext;

    class MockDataChannel extends EventTarget {
      send(raw) {
        const event = JSON.parse(raw);
        if (event.type !== 'response.create') return;
        setTimeout(() => {
          this.dispatchEvent(new MessageEvent('message', { data: JSON.stringify({
            type: 'response.output_audio_transcript.done',
            item_id: 'ai-1',
            transcript: 'Hãy giới thiệu một dự án kỹ thuật mà bạn tự hào.',
          }) }));
          this.dispatchEvent(new MessageEvent('message', { data: JSON.stringify({
            type: 'conversation.item.input_audio_transcription.completed',
            item_id: 'user-1',
            transcript: 'Tôi đã xây dựng một API FastAPI và cải thiện độ trễ.',
          }) }));
        }, 50);
      }
      close() {}
    }

    class MockPeerConnection {
      constructor() {
        this.connectionState = 'new';
        this.channel = new MockDataChannel();
      }
      addTrack() {}
      createDataChannel() {
        setTimeout(() => this.channel.dispatchEvent(new Event('open')), 20);
        return this.channel;
      }
      async createOffer() { return { type: 'offer', sdp: 'synthetic-local-sdp' }; }
      async setLocalDescription() {}
      async setRemoteDescription() {}
      close() {}
    }
    window.RTCPeerConnection = MockPeerConnection;
  });

  await page.route('https://api.openai.com/v1/realtime/calls', async (route) => {
    expect(route.request().headers().authorization).toBe('Bearer ek_synthetic_ephemeral');
    expect(route.request().postData()).toBe('synthetic-local-sdp');
    await route.fulfill({ status: 200, contentType: 'application/sdp', body: 'synthetic-remote-sdp' });
  });
  await mockBackend(page, async ({ request, url }) => {
    if (url.pathname === '/v1/interview/realtime/sessions/session-voice-1' && request.method() === 'GET') {
      return {
        body: {
          id: 'session-voice-1', application_id: 'app-1', status: 'ready',
          question_limit: 5, language: 'vi', consent_audio: true,
        },
      };
    }
    if (url.pathname.endsWith('/client-secret')) {
      return {
        body: {
          interview_session_id: 'session-voice-1',
          client_secret: 'ek_synthetic_ephemeral', expires_at: 9999999999,
          provider_session_id: 'provider-synthetic', model: 'gpt-realtime-test',
          voice: 'marin', configuration_version: 'realtime_session_vi_v2',
        },
      };
    }
    if (url.pathname.endsWith('/events')) {
      const payload = request.postDataJSON();
      expect(payload).not.toHaveProperty('client_secret');
      expect(payload.payload).not.toHaveProperty('sdp');
      return {
        status: 201,
        body: {
          event_id: `event-${payload.event_sequence}`,
          interview_session_id: 'session-voice-1',
          event_type: payload.event_type, event_sequence: payload.event_sequence,
          accepted: true, replayed: false, created_at: '2026-07-21T08:00:00Z',
        },
      };
    }
    if (url.pathname.endsWith('/complete')) {
      const payload = request.postDataJSON();
      expect(payload.turns[0].question_text).toContain('Hãy giới thiệu');
      expect(payload.turns[0].answer_transcript).toContain('Tôi đã xây dựng');
      return {
        body: {
          interview_session_id: 'session-voice-1', status: 'completed',
          completed_turns: 1, summary_status: 'ready', ended_at: '2026-07-21T08:01:00Z',
        },
      };
    }
    if (url.pathname.endsWith('/summary')) {
      return {
        body: {
          interview_session_id: 'session-voice-1', status: 'ready', language: 'vi',
          rubric_version: 'realtime_practice_v1', overall_score: 80,
          rubric: { relevance: { score: 4, max_score: 5 } },
          strengths: ['Câu trả lời có bằng chứng cụ thể.'], weaknesses: [],
          suggested_improvements: ['Dùng cấu trúc STAR ngắn gọn.'],
          next_practice_questions: ['Hãy mô tả một quyết định kỹ thuật.'],
          limitations: ['Không lưu âm thanh.'],
          disclaimer: 'Chỉ phục vụ luyện tập.',
        },
      };
    }
    return null;
  });

  await page.goto('/interview/sessions/session-voice-1/room');
  await page.getByRole('button', { name: /Bắt đầu phỏng vấn bằng giọng nói/i }).click();
  await expect(page.getByText('Đã kết nối', { exact: true })).toBeVisible();
  await expect(page.getByText('Hãy giới thiệu một dự án kỹ thuật mà bạn tự hào.').first()).toBeVisible();
  await expect(page.getByText('Tôi đã xây dựng một API FastAPI và cải thiện độ trễ.')).toBeVisible();
  expect(await page.evaluate(() => window.__micConstraints)).toEqual({ audio: true });
  expect(await page.evaluate(() => Object.values(localStorage).some((value) => value.includes('ek_synthetic')))).toBe(false);
  await page.getByRole('button', { name: 'Tắt microphone' }).click();
  await expect(page.getByRole('button', { name: 'Bật microphone' })).toBeVisible();
  await page.getByRole('button', { name: 'Kết thúc phiên' }).click();

  await expect(page).toHaveURL(/\/interview\/sessions\/session-voice-1\/summary$/);
  await expect(page.getByRole('heading', { name: 'Đánh giá buổi phỏng vấn' })).toBeVisible();
  await expect(page.getByText('Câu trả lời có bằng chứng cụ thể.')).toBeVisible();
  expect(browserErrors).toEqual([]);
});
