'use client';

import Link from 'next/link';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import PageShell from '@/components/common/PageShell';
import { trackEvent, ANALYTICS_EVENTS } from '@/lib/analytics';
import { useEffect } from 'react';

/**
 * Trang Trợ giúp / Hướng dẫn tĩnh.
 */

const FAQS = [
  {
    q: 'Tôi nên bắt đầu từ đâu?',
    a: 'Bắt đầu với Phân tích CV. Tải lên CV, dán mô tả công việc (JD) và chạy phân tích để nhận điểm phù hợp, kỹ năng đáp ứng/thiếu và đề xuất cải thiện.',
  },
  {
    q: 'Làm thế nào để phân tích CV so với mô tả công việc?',
    a: 'Mở Phân tích CV, tải lên file PDF hoặc DOCX, dán JD, chọn mức độ khắt khe và ngôn ngữ, sau đó bắt đầu phân tích. Kết quả sẽ hiển thị điểm phù hợp và kỹ năng còn thiếu.',
  },
  {
    q: 'Làm thế nào để tạo hồ sơ ứng tuyển?',
    a: 'Vào Hồ sơ ứng tuyển → Tạo mới. Nhập tên công ty, chức danh và mô tả công việc. Mỗi hồ sơ là một không gian làm việc cho một vị trí mục tiêu.',
  },
  {
    q: 'Làm thế nào để đính kèm phân tích vào hồ sơ ứng tuyển?',
    a: 'Mở hồ sơ ứng tuyển và chọn "Đính kèm phân tích". Chọn một phân tích đã hoàn thành gần đây từ danh sách, hoặc dán Job ID từ Lịch sử phân tích. Đính kèm sẽ mở khóa luyện phỏng vấn, thư xin việc và bộ hồ sơ.',
  },
  {
    q: 'Làm thế nào để luyện phỏng vấn?',
    a: 'Từ hồ sơ ứng tuyển đã đính kèm phân tích, mở Phỏng vấn. Trả lời từng câu hỏi AI tạo ra và xem phản hồi theo thang điểm. Các câu trả lời được lưu lại.',
  },
  {
    q: 'Làm thế nào để tạo thư xin việc hoặc bộ hồ sơ?',
    a: 'Từ hồ sơ ứng tuyển, mở Thư xin việc hoặc Bộ hồ sơ và nhấn Tạo. Cả hai đều cần có phân tích đã đính kèm. Thư xin việc có thể chỉnh sửa và lưu lại.',
  },
  {
    q: 'Những sự kiện phân tích nào được theo dõi?',
    a: 'Chỉ các sự kiện sản phẩm an toàn về quyền riêng tư (ví dụ: điều hướng trang, đăng nhập, bắt đầu/hoàn thành phân tích, tạo hồ sơ). Chúng tôi không bao giờ gửi nội dung CV, JD, câu trả lời phỏng vấn, thư xin việc, email hay mã định danh.',
  },
  {
    q: 'Tại sao dữ liệu demo nên là giả lập?',
    a: 'Khi trình bày, hãy sử dụng CV/JD giả lập và tài khoản demo. Không bao giờ trình bày dữ liệu ứng viên thật. Điều này bảo vệ quyền riêng tư và giữ cho bản demo có thể tái tạo.',
  },
];

export default function HelpPage() {
  const { isAuthChecking } = useRequireAuth();

  useEffect(() => {
    trackEvent(ANALYTICS_EVENTS.HELP_ASSISTANT_OPENED, { feature_name: 'help', source: 'help_page' });
  }, []);

  return (
    <PageShell isAuthChecking={isAuthChecking}>
      <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, color: 'var(--color-text)', marginBottom: '0.5rem' }}>
        Trợ giúp &amp; Hướng dẫn
      </h1>
      <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.6, marginBottom: '1.75rem', maxWidth: 640 }}>
        Hướng dẫn nhanh về quy trình AI CV Fit. Thực hiện từ trên xuống dưới:
        <strong> Phân tích CV → Kết quả → Hồ sơ ứng tuyển → Phỏng vấn → Thư xin việc → Bộ hồ sơ</strong>.
      </p>

      {/* Trợ lý AI */}
      <div style={{ background: 'linear-gradient(135deg, #EFF6FF, #F5F3FF)', border: '1px solid #BFDBFE', borderRadius: 'var(--radius-xl)', padding: '1.5rem', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '1.25rem', flexWrap: 'wrap', animation: 'fadeInUp 0.35s ease-out' }}>
        <div style={{ fontSize: '2.5rem', lineHeight: 1 }}>🤖</div>
        <div style={{ flex: 1, minWidth: 220 }}>
          <div style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--color-text)', marginBottom: '0.25rem' }}>
            Trợ lý AI
          </div>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.5, margin: 0 }}>
            Không biết nên làm gì tiếp? Hãy hỏi trợ lý AI — nó sẽ đọc hồ sơ, phân tích và nhiệm vụ học tập của bạn để đưa ra hướng dẫn cá nhân hóa.
          </p>
        </div>
        <Link
          href="/help/assistant"
          id="open-ai-assistant-btn"
          style={{ display: 'inline-flex', alignItems: 'center', gap: '0.375rem', padding: '0.625rem 1.25rem', background: 'linear-gradient(135deg, var(--color-primary), #4F46E5)', color: 'white', borderRadius: 'var(--radius-md)', fontWeight: 600, fontSize: 'var(--font-size-sm)', textDecoration: 'none', whiteSpace: 'nowrap', flexShrink: 0 }}
        >
          Mở trợ lý →
        </Link>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem', marginBottom: '2rem' }}>
        {FAQS.map((item, i) => (
          <div
            key={i}
            style={{ border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', padding: '1rem 1.25rem', background: 'var(--color-surface, #fff)' }}
          >
            <div style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--color-text)', marginBottom: '0.375rem' }}>
              {item.q}
            </div>
            <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.7, margin: 0 }}>
              {item.a}
            </p>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', fontSize: 'var(--font-size-sm)' }}>
        <Link href="/dashboard" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>Phân tích CV</Link>
        <span style={{ color: 'var(--color-text-muted)' }}>·</span>
        <Link href="/applications" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>Hồ sơ ứng tuyển</Link>
        <span style={{ color: 'var(--color-text-muted)' }}>·</span>
        <Link href="/profile/evidence" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>Kho bằng chứng</Link>
        <span style={{ color: 'var(--color-text-muted)' }}>·</span>
        <Link href="/learning" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>Học tập</Link>
        <span style={{ color: 'var(--color-text-muted)' }}>·</span>
        <Link href="/help/assistant" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>Trợ lý AI</Link>
      </div>
    </PageShell>
  );
}
