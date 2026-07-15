# Interview Realtime QA Checklist — Phase 8 Master Tracker

> **Owner:** Đạt
> **Date:** 2026-07-15
> **Status:** IN_PROGRESS
> **Purpose:** Single source of truth for all QA/privacy/evaluation tasks for Phase 8

---

## Overview

| Track | Doc | Status |
|-------|-----|--------|
| Guardrails | `docs/interview_realtime_guardrails.md` | ⏳ IN PROGRESS |
| Privacy Review | `docs/interview_video_privacy_review.md` | ⏳ IN PROGRESS |
| Backend Tests | `backend/tests/test_interview_realtime.py` | ⏳ IN PROGRESS |
| Privacy Tests | `backend/tests/test_interview_realtime_privacy.py` | ⏳ IN PROGRESS |
| Evaluation Cases | `evaluation/cases/interview_realtime/` | ⏳ IN PROGRESS |
| Browser QA | This doc §3 | ⏳ PENDING |
| Consent QA | This doc §4 | ⏳ PENDING |
| Realtime Failure QA | This doc §5 | ⏳ PENDING |
| Team Sign-off | This doc §6 | ⏳ PENDING |

---

## 1. Backend Privacy Tests Checklist

Run after `test_interview_realtime_privacy.py` is created:

```
cd backend && python -m pytest tests/test_interview_realtime_privacy.py -v
```

| Test | Expected | Status |
|------|---------|--------|
| Session creation requires auth | 401 unauthed | ⏳ |
| Ephemeral token returned only to session owner | 403 for others | ⏳ |
| Transcript not in analytics event payload | No transcript key | ⏳ |
| Raw media not in logs | No audio/video in log output | ⏳ |
| Consent required before audio capture | `consent_audio=false` → 400 or blocked | ⏳ |
| Cross-user session access → 404 | Session owner isolation | ⏳ |
| Session delete removes media | Media records deleted | ⏳ |
| Feature flag off → 404 | `ENABLE_PHASE8_REALTIME=false` | ⏳ |

---

## 2. Grep / Privacy Scan Checklist

Run these commands after backend and frontend code exist:

### 2.1 OpenAI API Key Not in Frontend

```bash
rg -i "OPENAI_API_KEY|sk-|openai.*key" \
  frontend/src/
# Expected: no matches
```

### 2.2 No Raw Transcript in Analytics

```bash
rg -i "transcript|answer_text|audio|video" \
  frontend/src/lib/analytics.js
# Expected: only event name constants, no raw data
```

### 2.3 Ephemeral Token Pattern in Frontend

```bash
rg -i "ephemeral|client_secret|realtime_token" \
  frontend/src/
# Expected: safe usage only (API call params)
```

### 2.4 No Raw Media in Backend Logs

```bash
rg -i "audio|video|transcript" \
  backend/app/services/interview_realtime/
# Expected: storage_key references only, no raw data
```

### 2.5 No Emotion/Personality Inference Keywords

```bash
rg -i "nervous|honest|personality|emotion|truthful|protected" \
  backend/app/services/interview_realtime/ \
  frontend/src/app/interview/
# Expected: no matches (except in guardrails test assertions)
```

---

## 3. Browser Compatibility QA ⏳ PENDING

Test on these browsers:

| Browser | Version | Microphone | Camera | WebRTC | Status |
|---------|---------|-----------|--------|--------|--------|
| Chrome | Latest | ⏳ | ⏳ | ⏳ | ⏳ |
| Edge | Latest | ⏳ | ⏳ | ⏳ | ⏳ |
| Firefox | Latest | ⏳ | ⏳ | ⏳ | ⏳ |
| Safari | Latest | ⏳ | ⏳ | ⏳ | ⏳ |

### Browser QA Steps

#### Microphone Flow

- [ ] Microphone permission prompt appears when starting interview
- [ ] Allow microphone → permission granted
- [ ] Deny microphone → Vietnamese error message shown
- [ ] After deny → text fallback option appears
- [ ] Microphone meter shows input level when active

#### Camera Flow

- [ ] Camera permission prompt appears (optional step)
- [ ] Enable camera → preview shows in panel
- [ ] Deny camera → audio-only interview continues
- [ ] Camera preview shows correct aspect ratio
- [ ] Camera can be toggled off mid-session

#### WebRTC Connection

- [ ] Connection status indicator visible during setup
- [ ] "Connecting..." state shown
- [ ] "Connected" state shown when ready
- [ ] AI interviewer greeting plays
- [ ] Connection latency < 3s on stable network

#### Interview Flow

- [ ] AI asks first question
- [ ] User can speak answer
- [ ] Live transcript appears in real-time
- [ ] User can see AI is listening
- [ ] AI asks follow-up question
- [ ] User can end session early
- [ ] Session summary appears after end

#### Transcript Panel

- [ ] Transcript panel shows question text
- [ ] Transcript panel shows answer text
- [ ] Turn separator visible between Q&A pairs
- [ ] No raw CV/JD text in transcript
- [ ] No raw media in transcript panel

---

## 4. Consent QA Checklist ⏳ PENDING

### 4.1 Consent Screen Content

- [ ] Vietnamese consent message for microphone
- [ ] Vietnamese consent message for camera
- [ ] Audio processing disclosure present
- [ ] Camera optional disclaimer present
- [ ] Video recording optional disclaimer present
- [ ] AI feedback disclaimer present
- [ ] "Do not share sensitive info" warning present

### 4.2 Consent Behavior

- [ ] Interview cannot start without audio consent
- [ ] Camera can be skipped
- [ ] Recording can be skipped
- [ ] Consent stored with session
- [ ] Consent can be withdrawn mid-session → session ends gracefully

### 4.3 Permission Denied Flow

- [ ] Microphone denied → Vietnamese message: "Microphone access is required for voice interview."
- [ ] Message includes: "You can retry permission or switch to text practice."
- [ ] Text practice fallback button visible
- [ ] Camera denied → "Continue with audio-only interview. Camera is optional." shown
- [ ] No crash or error page on permission denied

---

## 5. Realtime Failure Cases QA ⏳ PENDING

| # | Case | Expected Behavior | Status |
|---|------|----------------|--------|
| RF-01 | Microphone permission denied | Vietnamese error + text fallback option | ⏳ |
| RF-02 | Camera permission denied | Continue audio-only | ⏳ |
| RF-03 | WebRTC connection fails (network) | Show error + retry button | ⏳ |
| RF-04 | AI disconnects mid-session | Show reconnect option | ⏳ |
| RF-05 | User disconnects mid-session | Session state preserved | ⏳ |
| RF-06 | Network unstable | Show reconnect + "poor connection" indicator | ⏳ |
| RF-07 | Browser not support WebRTC | Show fallback message | ⏳ |
| RF-08 | Session timeout (30 min inactivity) | Session marked `aborted` | ⏳ |
| RF-09 | Reconnect within 5 min | Session restored | ⏳ |
| RF-10 | Reconnect after 5 min | Session ended, summary available | ⏳ |

---

## 6. Rubric Evaluation Checklist ⏳ PENDING

### 6.1 Score Ranges

| Answer Type | Expected Score Pattern | Status |
|-------------|----------------------|--------|
| Strong specific answer | High relevance + specificity + evidence | ⏳ |
| Vague answer | Low relevance + specificity | ⏳ |
| No answer / too short | Low across all dimensions | ⏳ |
| Off-topic answer | Low relevance | ⏳ |
| Excellent STAR behavioral | High structure + relevance | ⏳ |

### 6.2 Feedback Quality

- [ ] Strong answer → at least one strength noted
- [ ] Weak answer → non-empty `missing_evidence` field
- [ ] Weak answer → non-empty `suggested_improvements` field
- [ ] Every feedback → `disclaimer` field present
- [ ] `risk` score not labeled truthfulness
- [ ] Feedback references transcript by turn, not by embedding text

### 6.3 Gap Question Feedback

- [ ] Gap question: "no evidence was found in your CV"
- [ ] Gap question: does NOT say "you don't know FastAPI"
- [ ] Gap question: suggests action, not judgment

---

## 7. Evaluation Cases Summary ⏳ PENDING

`evaluation/cases/interview_realtime/`

| Category | Target | Created | Status |
|----------|--------|---------|--------|
| Technical questions | 5 | ⏳ | ⏳ |
| Behavioral questions | 5 | ⏳ | ⏳ |
| Project deep-dive questions | 5 | ⏳ | ⏳ |
| Gap-check questions | 3 | ⏳ | ⏳ |
| Weak answer feedback | 3 | ⏳ | ⏳ |
| Strong answer feedback | 3 | ⏳ | ⏳ |
| Permission denied cases | 2 | ⏳ | ⏳ |
| Realtime disconnect cases | 2 | ⏳ | ⏳ |
| **Total minimum** | **28** | ⏳ | ⏳ |

---

## 8. Demo Script ⏳ PENDING

Execute this demo script end-to-end:

```
1. Login as demo user.
2. Open Target Job detail.
3. Click Start AI Interview.
4. Choose Mixed interview, Medium difficulty, 5 questions.
5. Allow microphone.
6. Enable camera preview (optional).
7. Start interview.
8. AI greets user and asks question.
9. User answers by voice.
10. Transcript appears.
11. AI asks follow-up.
12. User answers again.
13. End session.
14. Show summary:
    - overall score
    - rubric
    - strengths
    - weak areas
    - suggested answers
    - learning tasks
15. Open learning roadmap task generated from weak answer.
```

Expected outcomes per step → record PASS/FAIL in closeout report.

---

## 9. Team Sign-off ⏳ PENDING

### Pre-sign-off Checklist

- [ ] All backend privacy tests PASS
- [ ] All grep/privacy scans PASS
- [ ] Browser compatibility QA PASS (4 browsers)
- [ ] Consent QA PASS
- [ ] Realtime failure cases PASS
- [ ] Rubric evaluation PASS
- [ ] Evaluation cases PASS (28/28 minimum)
- [ ] Demo script PASS end-to-end
- [ ] `ENABLE_PHASE8_REALTIME` feature flag documented

### Sign-off

| Role | Name | Status |
|------|------|--------|
| Backend | Phúc | ☐ |
| Frontend | Quân | ☐ |
| QA/Privacy | Đạt | ☐ |

---

## 10. Command Reference

```bash
# Backend privacy tests
cd backend && python -m pytest tests/test_interview_realtime_privacy.py -v

# Backend all Phase 8 tests
cd backend && python -m pytest tests/test_interview_realtime.py -v

# Grep: OpenAI key in frontend
rg -i "OPENAI_API_KEY|sk-" frontend/src/

# Grep: raw transcript in analytics
rg -i "transcript|answer_text|audio|video" frontend/src/lib/analytics.js

# Grep: emotion/personality inference
rg -i "nervous|honest|personality|emotion|truthful" \
  backend/app/services/interview_realtime/ \
  frontend/src/app/interview/

# Evaluation: Phase 8 cases
python scripts/evaluate_interview_realtime_cases.py
```

---

*Last updated: 2026-07-15 by Đạt*
