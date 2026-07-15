# Interview Realtime — Video & Privacy Review

**Date:** 2026-07-15
**Owner:** Đạt
**Status:** IN_PROGRESS
**Gates:** Must pass before `ENABLE_PHASE8_REALTIME=true`

---

## Purpose

This document reviews the privacy and safety posture of the Phase 8 Interview Realtime feature: OpenAI Realtime API via WebRTC, microphone/camera handling, transcript storage, ephemeral tokens, and multimodal feedback. It identifies risks and defines the conditions required to flip `ENABLE_PHASE8_REALTIME` to `true`.

---

## Privacy Risk Matrix

| Feature | Risk | Severity | Status | Notes |
|---------|------|----------|--------|-------|
| OpenAI API key in frontend | Raw key exposed | 🔴 Critical | ⏳ | Must use ephemeral token only |
| Ephemeral token logging | Token leaked | 🔴 Critical | ⏳ | Token must not appear in logs |
| Microphone access without consent | Privacy violation | 🔴 Critical | ⏳ | Consent required before capture |
| Raw transcript in analytics | CV/JD leaked | 🔴 Critical | ⏳ | Only turn_index, question_type allowed |
| Raw audio/video in analytics | Media leaked | 🔴 Critical | ⏳ | Media must not appear in events |
| Raw media in server logs | Media leaked | 🔴 Critical | ⏳ | Storage keys only in logs |
| Emotion inference | Bias/discrimination | 🔴 Critical | ⏳ | Forbidden by guardrails |
| Personality inference | Bias/discrimination | 🔴 Critical | ⏳ | Forbidden by guardrails |
| Truthfulness detection | False accusation | 🔴 Critical | ⏳ | Forbidden; risk != truthfulness |
| Protected attribute inference | Discrimination | 🔴 Critical | ⏳ | Forbidden by guardrails |
| Hiring probability prediction | Misleading | 🔴 Critical | ⏳ | Forbidden by guardrails |
| Media stored without consent | Privacy violation | 🔴 Critical | ⏳ | `consent_recording` required |
| Cross-user session access | Data leak | 🔴 Critical | ⏳ | Session owner isolation enforced |
| Realtime disconnect without recovery | User blocked | 🟠 High | ⏳ | Reconnect option must exist |
| Feature flag off → 500 | Service error | 🟠 High | ⏳ | Flag off → 404, not 500 |

---

## 1. Token & API Key Security

### OpenAI API Key

- [ ] OpenAI API key must never be stored in frontend code.
- [ ] OpenAI API key must never be sent to frontend.
- [ ] OpenAI API key must never appear in frontend environment variables.
- [ ] Only ephemeral client secret may be sent to frontend.

### Ephemeral Token

- [ ] Ephemeral token created server-side via OpenAI client secret API.
- [ ] Token TTL must be short (max 3600 seconds).
- [ ] Token returned only to authenticated session owner.
- [ ] Token must not be logged in server logs.
- [ ] Token must not be included in analytics events.
- [ ] Token must not be included in error messages shown to user.

**Verification commands:**
```bash
# Must return no results
rg -i "OPENAI_API_KEY|sk-" frontend/src/

# Must only find safe API call parameter
rg -i "ephemeral|client_secret" backend/app/services/interview_realtime/
```

---

## 2. Media Consent & Handling

### Consent Requirements

- [ ] Consent screen shown before any microphone/camera access.
- [ ] `consent_audio` must be `true` before audio capture.
- [ ] `consent_camera` is optional; camera accessed only if `true`.
- [ ] `consent_recording` is optional; media stored only if `true`.
- [ ] Consent values stored with session record.
- [ ] User can withdraw consent mid-session → session ends gracefully.

### Consent Copy (Vietnamese)

Required Vietnamese text elements:

```
1. "Phòng phỏng vấn này sử dụng microphone và có thể sử dụng camera."
2. "Âm thanh được xử lý để tạo transcript và phản hồi phỏng vấn."
3. "Camera là tùy chọn."
4. "Ghi hình video là tùy chọn và mặc định không bật."
5. "Phản hồi AI chỉ dùng để luyện tập, không đảm bảo kết quả tuyển dụng."
6. "Không chia sẻ thông tin nhạy cảm cá nhân trong buổi phỏng vấn."
7. "Tôi đồng ý cho microproces âm thanh để luyện tập phỏng vấn."
```

### Media Storage

- [ ] Audio/video stored only if `consent_recording=true`.
- [ ] Media stored with `storage_key` reference, not raw bytes in DB.
- [ ] Media artifacts linked to `session_id` and `turn_id`.
- [ ] Media can be deleted by session owner.
- [ ] Media deletion is permanent.
- [ ] No media stored in server logs.
- [ ] No media stored in analytics events.

---

## 3. Transcript Privacy

### Transcript Storage

- [ ] Transcript generated only if `consent_audio=true`.
- [ ] Transcript stored linked to `turn_id` and `session_id`.
- [ ] Raw transcript must not appear in analytics events.
- [ ] Raw transcript must not appear in server logs.
- [ ] Raw transcript must not appear in admin views.
- [ ] Transcript accessible only to session owner.

### Transcript in Responses

- [ ] `GET /v1/interview/realtime/sessions/{id}` may return transcript for owner view only.
- [ ] Summary endpoint must not include raw transcript text.
- [ ] GA4 events must not include transcript fields.

**Forbidden transcript analytics fields:**
```
transcript_text
answer_transcript
raw_transcript
audio_transcript
```

---

## 4. Analytics Privacy

### Allowed Analytics Fields

Only these low-cardinality, non-sensitive fields are allowed in interview realtime events:

```
event_name
session_id          # internal only, hashed or UUID
turn_index
question_type       # technical | behavioral | project | hr | gap_check
difficulty          # easy | medium | hard
overall_bucket      # "0_20" | "20_40" | "40_60" | "60_80" | "80_100"
fallback_used       # boolean
intent              # for help assistant integration
feature_name
route
```

### Forbidden Analytics Fields

```
raw_transcript
answer_text
audio
video
transcript
score
fit_score
emotion
personality
truthfulness
protected_attribute
cv_text
jd_text
```

### GA4 Event List

| Event Name | Allowed Params |
|-----------|---------------|
| `interview_realtime_session_created` | session_id, interview_type, difficulty |
| `interview_realtime_consent_given` | consent_audio, consent_camera, consent_recording |
| `interview_realtime_connected` | session_id |
| `interview_realtime_turn_completed` | session_id, turn_index, question_type |
| `interview_realtime_feedback_viewed` | session_id, overall_bucket |
| `interview_realtime_session_ended` | session_id, duration_bucket |
| `interview_realtime_disconnect` | session_id, reason |
| `interview_realtime_permission_denied` | permission_type (audio \| camera) |
| `interview_realtime_fallback_used` | session_id, fallback_type |

---

## 5. Feedback Safety

### Forbidden Feedback Language

These must never appear in any AI-generated feedback:

```
"You looked nervous."
"You seemed stressed."
"You seem dishonest."
"You are not telling the truth."
"You have low confidence."
"You seem introverted."
"You seem like a leader."
"You are unlikely to be hired."
"Your personality is not suitable."
"You seem [age/gender/ethnicity]."
```

### Allowed Feedback Language

```
"Your answer was clear but needs more specific project evidence."
"You mentioned PostgreSQL, but did not explain your schema/design choices."
"Try using STAR structure for behavioral answers."
"Your answer was too short to assess technical depth."
"No evidence of FastAPI was found in your CV for this question."
```

### Disclaimer Requirement

Every feedback and summary response must include:

```
disclaimer: "This feedback is for practice only and does not guarantee hiring outcomes. Feedback is based on transcript evidence and known CV/JD data."
```

---

## 6. Session Security

### Ownership Enforcement

- [ ] Session creation requires authenticated user.
- [ ] Session owner `user_id` enforced on all session endpoints.
- [ ] Ephemeral token returned only to session owner.
- [ ] Cross-user session access returns 404 (not 403, to avoid existence disclosure).
- [ ] Turn data scoped to session owner.
- [ ] Summary accessible only to session owner.

### Feature Flag

- [ ] `ENABLE_PHASE8_REALTIME=false` returns 404 on all Phase 8 endpoints.
- [ ] Feature flag must be explicitly set in environment.
- [ ] Flag-off state must not cause 500 errors.

---

## 7. Realtime Disconnect & Failure Handling

### Disconnect Types

| Scenario | Behavior | Status |
|---------|---------|--------|
| User disconnects mid-session | Session state preserved as `active` | ⏳ |
| AI disconnects mid-session | Show reconnect option within 5 min | ⏳ |
| Network unstable | Show "poor connection" indicator + reconnect | ⏳ |
| Browser doesn't support WebRTC | Show fallback message + text option | ⏳ |
| Session timeout (30 min inactive) | Mark session `aborted` | ⏳ |
| Reconnect within 5 min | Restore session | ⏳ |
| Reconnect after 5 min | End session, summary available | ⏳ |

### Fallback Flow

When realtime connection fails:

```
Realtime connection failed
→ app switches to recorded-answer fallback
→ user records answer
→ backend transcribes audio
→ backend scores answer
→ user still receives feedback
```

---

## 8. Media Deletion & Retention

### Deletion Requirements

- [ ] Session owner can request deletion of all media for a session.
- [ ] Deletion request removes all `interview_media_artifacts` records for the session.
- [ ] Deletion must be permanent (no soft delete for media).
- [ ] Deletion confirmation shown to user.
- [ ] Deleted media links return 404.

### Retention Policy

- [ ] Transcript retained while session is active.
- [ ] Transcript deleted when session is deleted by owner.
- [ ] Media retained per consent — if `consent_recording=false`, no media stored.
- [ ] Transcript not included in analytics long-term storage.

---

## 9. Privacy Review Sign-off

### Checkpoint Results

| Checkpoint | Owner | Status | Date | Notes |
|-----------|--------|--------|------|-------|
| OpenAI key not in frontend | Đạt | ⏳ | — | |
| Ephemeral token never logged | Đạt | ⏳ | — | |
| Consent required before audio | Đạt | ⏳ | — | |
| Consent copy Vietnamese verified | Đạt | ⏳ | — | |
| No raw transcript in analytics | Đạt | ⏳ | — | |
| No raw media in analytics | Đạt | ⏳ | — | |
| No raw media in logs | Đạt | ⏳ | — | |
| No emotion/personality inference | Đạt | ⏳ | — | |
| No truthfulness detection | Đạt | ⏳ | — | |
| Session owner isolation | Đạt | ⏳ | — | |
| Feature flag gates routes | Đạt | ⏳ | — | |
| Disclaimer in every feedback | Đạt | ⏳ | — | |
| Media deletion works | Đạt | ⏳ | — | |
| Disconnect recovery tested | Đạt | ⏳ | — | |
| Final gate: `ENABLE_PHASE8_REALTIME=true` | Đạt + Phúc | ⏳ | — | |

---

## 10. Grep Verification Commands

After Phase 8 code exists, run these grep scans:

```bash
# 1. OpenAI key not in frontend — must return no results
rg -i "OPENAI_API_KEY|sk-|openai.*key" frontend/src/

# 2. Raw transcript in analytics — must return no results
rg -i "transcript|answer_text" frontend/src/lib/analytics.js

# 3. Emotion/personality inference — must return no results
rg -i "nervous|honest|personality|truthful" \
  backend/app/services/interview_realtime/ \
  frontend/src/app/interview/

# 4. Raw media in logs — must return no results
rg -i "audio|video" backend/app/services/interview_realtime/

# 5. Ephemeral token safe usage — check only
rg -i "ephemeral|client_secret" backend/app/services/interview_realtime/
# Must only find token creation/storage, not logging
```

---

*This document must pass all checkpoints before `ENABLE_PHASE8_REALTIME` is flipped to `true`.*
