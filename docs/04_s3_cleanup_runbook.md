# S3 Lifecycle Cleanup Runbook — AI CV Fit

## Mục tiêu

CV và report có thể chứa dữ liệu cá nhân, nên cần chính sách dọn file:
- xóa file tạm sau một khoảng thời gian,
- abort incomplete multipart upload,
- tránh bucket phình chi phí,
- tránh giữ CV thô lâu hơn cần thiết.

## Prefix đề xuất

```text
uploads/raw-cv/
reports/
tmp/
```

## Lifecycle policy đề xuất

Lưu thành `infra/s3-lifecycle.json`:

```json
{
  "Rules": [
    {
      "ID": "expire-temporary-uploads",
      "Status": "Enabled",
      "Filter": { "Prefix": "tmp/" },
      "Expiration": { "Days": 1 }
    },
    {
      "ID": "expire-raw-cv-uploads",
      "Status": "Enabled",
      "Filter": { "Prefix": "uploads/raw-cv/" },
      "Expiration": { "Days": 30 }
    },
    {
      "ID": "expire-generated-reports",
      "Status": "Enabled",
      "Filter": { "Prefix": "reports/" },
      "Expiration": { "Days": 30 }
    },
    {
      "ID": "abort-incomplete-multipart-uploads",
      "Status": "Enabled",
      "Filter": { "Prefix": "" },
      "AbortIncompleteMultipartUpload": {
        "DaysAfterInitiation": 7
      }
    }
  ]
}
```

## Apply bằng AWS CLI

```powershell
aws s3api put-bucket-lifecycle-configuration `
  --bucket 2026-fpt-exe-app `
  --region ap-southeast-2 `
  --lifecycle-configuration file://infra/s3-lifecycle.json
```

## Kiểm tra lại

```powershell
aws s3api get-bucket-lifecycle-configuration `
  --bucket 2026-fpt-exe-app `
  --region ap-southeast-2
```

## Checklist privacy

- Không log raw CV text.
- Không log S3 signed URL/token.
- Không expose `local_path`.
- Report download chỉ qua access_token.
- Raw CV có TTL.
- Generated report có TTL.
- Incomplete multipart upload được abort.

## Ghi chú quyết định

Với Phase 1, 30 ngày cho raw CV/report là đủ để user quay lại lấy kết quả demo. Sang Phase 2 khi có account/history, cần tách:
- user-owned retained reports,
- temporary guest reports,
- deleted/anonymized raw CV.
