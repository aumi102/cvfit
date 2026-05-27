# Tin nhắn gửi Quân

Quân ơi, frontend Phase 1 mình chỉ cần đạt scope tối thiểu để chốt demo, chưa cần login/dashboard phức tạp.

Yêu cầu chính:

1. Landing page giới thiệu sản phẩm.
2. Trang analyze gồm upload CV + paste JD.
3. Gọi backend Render API qua env `NEXT_PUBLIC_API_BASE_URL`.
4. Sau khi create-score, lưu `job_id` + `access_token`.
5. Có loading state khi job queued/running.
6. Poll status đến khi succeeded/failed.
7. Hiển thị result dashboard cơ bản khi succeeded.
8. Download report được với `access_token`.
9. Không `console.log(access_token)`.
10. Có error state rõ nếu upload/job/result/download fail.

Chưa cần làm:
- login,
- history dashboard,
- recruiter dashboard,
- design quá phức tạp,
- payment.

Jinja UI backend vẫn giữ làm fallback cho đến khi Next gọi được backend thật. Mục tiêu trước thứ Bảy là demo ổn, không phải full product.
