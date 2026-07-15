# Interview Realtime — Guardrails v5

**Version:** 5.0
**Date:** 2026-07-15
**Owner:** Đạt (evaluation / QA)
**Status:** DRAFT — Active Phase 8
**Extends:** Guardrails v4 (Phase 6)

---

## Purpose

This document defines Phase 8 guardrails for the Real-time AI Interview Room feature. It extends Guardrails v4 with rules specific to voice/video interaction, WebRTC, transcript storage, ephemeral tokens, and multimodal interview feedback. All v4 rules remain in force.

---

## Guardrail Philosophy

> The system must **never fabricate** a skill, experience, or attribute — in any output type, at any phase. The interview room processes live audio and generates transcript-derived feedback. Every claim in system-generated feedback must be traceable to transcript evidence or CV/JD evidence. The system must not infer personality, emotion, truthfulness, protected attributes, or hiring probability from voice, video, or transcript.

---

## 1. Realtime Session Guardrails

### Session Creation

- [ ] Session must be scoped to the authenticated caller's `user_id`.
- [ ] Session may optionally link to a `target_job_id`, `application_id`, or `analysis_job_id`.
- [ ] Session mode must be one of: `realtime_voice`, `audio_fallback`, `video_optional`.
- [ ] Consent fields (`consent_audio`, `consent_camera`, `consent_recording`) must be recorded before session starts.
- [ ] `consent_audio` must be `true` before any audio is captured or transmitted.
- [ ] `consent_camera` is optional; if `false`, camera must not be accessed.
- [ ] `consent_recording` is optional; if `false`, video/audio must not be stored.

### Ephemeral Token

- [ ] OpenAI API key must never be stored in frontend code or environment.
- [ ] Ephemeral client secret must be created server-side and returned to the session owner only.
- [ ] Ephemeral token must have a short TTL (e.g., 3600 seconds).
- [ ] Ephemeral token must not be logged in any server or client log.
- [ ] Session owner must be verified before issuing the ephemeral token.

### Session Lifecycle

- [ ] Session status transitions: `setup` → `active` → `completed` | `aborted` | `failed`.
- [ ] Only session owner can start, end, or abort their own session.
- [ ] Abandoned sessions (no activity > 30 min) should be marked `aborted`.
- [ ] Session audio/video artifacts must not be stored unless `consent_recording=true`.
- [ ] Deleted session must not leave orphaned media artifacts.

---

## 2. Transcript & Turn Guardrails

### Transcript Generation

- [ ] Transcript text is generated from audio input via OpenAI Realtime API.
- [ ] Transcript must be stored linked to the session `turn_id`.
- [ ] Raw transcript must not appear in any analytics event.
- [ ] Raw transcript must not appear in any API response field outside the transcript-specific endpoint.
- [ ] Transcript storage must respect `consent_audio=true`.
- [ ] If `consent_audio=false`, transcript must not be generated.

### Turn Tracking

- [ ] Each question-answer turn must be tracked with a `turn_index`.
- [ ] Turn must link to a `question_type`: `technical`, `behavioral`, `project`, `hr`, `gap_check`.
- [ ] Turn must store `question_text` and optionally `answer_transcript`.
- [ ] Turn must not store raw audio bytes.
- [ ] Follow-up question (`ai_followup_text`) must be generated only from transcript evidence, not from personality inference.

### Question Generation

- [ ] Questions must be grounded in the attached analysis (JD requirements + CV evidence).
- [ ] `gap_probe` questions must state the skill was not found; must not imply the user has the skill.
- [ ] Questions must not ask about skills not mentioned in the JD.
- [ ] `why_this_question` must reference a real JD requirement or CV evidence line.
- [ ] Questions must not embed raw CV or JD text.
- [ ] Difficulty level must match evidence depth in CV (junior → junior questions).

---

## 3. Feedback & Scoring Guardrails

### Rubric Scoring

- [ ] Scoring must be rule-based (deterministic); no floating LLM scoring without evaluation coverage.
- [ ] Score range must be 0–100.
- [ ] Rubric dimensions: `relevance`, `specificity`, `evidence`, `structure`, `technical_depth`, `communication_clarity`, `risk`.
- [ ] `risk` score means: higher risk = answer may be vague, unsupported, or inconsistent with known CV evidence.
- [ ] `risk` must NOT be labeled or described as "truthfulness detection."
- [ ] Feedback must reference transcript text by turn/turn_index, not by embedding raw transcript.
- [ ] Feedback must not fabricate evidence or claim the user has skills not mentioned in CV/JD.

### Feedback Wording — Allowed

```
"Your answer was clear but needs more specific project evidence."
"You mentioned PostgreSQL, but did not explain your schema/design choices."
"Try using STAR structure for behavioral answers."
"Your answer was too short to assess technical depth."
```

### Feedback Wording — Forbidden

```
"You looked nervous."
"You seem dishonest."
"You have low confidence."
"You are unlikely to be hired."
"Your personality is not suitable."
"You are not telling the truth."
```

### Disclaimer

- [ ] Every feedback response must include a non-empty `disclaimer` field.
- [ ] Disclaimer must state: "This feedback is for practice only and does not guarantee hiring outcomes."
- [ ] Disclaimer must state: "Feedback is based on transcript evidence and known CV/JD data."

---

## 4. Privacy Guardrails

### No Sensitive Inference

The following are strictly forbidden and must not appear in any output or analytics:

- [ ] Emotion inference from voice or video (e.g., "you sounded nervous", "you looked stressed")
- [ ] Personality inference (e.g., "you seem introverted", "you have leadership potential")
- [ ] Truthfulness detection (e.g., "you are lying", "your answer is not truthful")
- [ ] Protected attribute inference (age, gender, ethnicity, religion, disability, sexual orientation, etc.)
- [ ] Hiring probability prediction from voice, video, or transcript
- [ ] Sentiment scoring beyond relevance/specificity/evidence/structure

### Media Handling

- [ ] No audio/video storage unless `consent_recording=true`.
- [ ] No raw media bytes in analytics events.
- [ ] No raw media bytes in server logs.
- [ ] Media artifacts must be deletable by the session owner.
- [ ] Media deletion must be permanent.

### Transcript Privacy

- [ ] Raw transcript text must not appear in GA4 event payloads.
- [ ] Raw transcript text must not appear in server logs.
- [ ] Raw transcript text must not appear in admin views.
- [ ] Transcript may appear in user-facing summary (within the session owner view only).

### Analytics Privacy

Allowed analytics fields for interview realtime:

```
event_name
session_id (hashed or internal only)
turn_index
question_type
difficulty
overall_bucket       # e.g. "60_80", not exact score
fallback_used
intent
```

Forbidden analytics fields:

```
raw_transcript
answer_text
audio
video
score
fit_score
emotion
personality
truthfulness
protected_attribute
```

---

## 5. AI Interviewer Behavior

### Role Definition

- [ ] AI interviewer role: "AI interview coach" — professional, neutral.
- [ ] AI must ask one question at a time.
- [ ] AI must not ask sensitive personal questions (salary expectation only if role-relevant; do not pressure).
- [ ] AI must not infer protected attributes.
- [ ] AI must not guarantee hiring outcomes.
- [ ] AI must ask follow-up only based on transcript evidence, not personality inference.
- [ ] AI must end interview after configured number of questions.

### Session Configuration

```
voice: stable voice (do not change mid-session)
turn_detection: server_vad if available
input_audio_transcription: enabled
modalities: audio + text
max_turns: configurable (default 5)
interview_type: technical | behavioral | project | hr | mixed
```

---

## 6. Interview Types Guardrails

### Technical

- [ ] Focus on JD-required skills, technical gaps, project evidence, tools/frameworks.
- [ ] Do not ask about skills not in JD.
- [ ] Gap questions must say "no evidence was found in your CV" not "you don't know".

### Behavioral

- [ ] Focus on teamwork, challenge, learning ability, ownership, communication.
- [ ] Do not infer personality traits.
- [ ] Do not link behavioral answers to protected attributes.

### Project Deep-dive

- [ ] Focus on CV projects, architecture, tradeoffs, impact, limitations.
- [ ] Questions must reference projects mentioned in CV by name/description, not by embedding raw CV text.
- [ ] Do not ask about projects not in CV.

### HR

- [ ] Focus on motivation, role fit, career goals, availability.
- [ ] Salary expectation: optional only if role-relevant; do not score based on answer.
- [ ] Do not probe protected attributes through indirect questions.

### Mixed

- [ ] Combination for demo purposes.
- [ ] Must rotate through technical/behavioral/project appropriately.

---

## 7. Summary & Report Guardrails

### Session Summary

- [ ] Summary must include `overall_score` (0–100).
- [ ] Summary must include `rubric_json` with all 7 dimensions.
- [ ] Summary must include `strengths` and `weaknesses` as string arrays.
- [ ] Summary must include `suggested_improvements` as string array.
- [ ] Summary must include `next_questions` as string array.
- [ ] Summary must include `learning_tasks` as structured array.
- [ ] Summary must include `disclaimer` field.

### Learning Task Generation

- [ ] Learning tasks from interview weak areas must use `skill` names from analysis only.
- [ ] Tasks must not claim the user has a skill they scored poorly on.
- [ ] Tasks must use "no evidence was found" wording for weak areas.
- [ ] Task priority must derive from gap severity, not from personality inference.

### Report Export

- [ ] Export must not include raw transcript text.
- [ ] Export must not include audio/video.
- [ ] Export must include disclaimer.
- [ ] Export must not include session token, ephemeral credential, or API key.

---

## 8. Feature Flag & Rollback

- [ ] `ENABLE_PHASE8_REALTIME` feature flag must gate all Phase 8 routes.
- [ ] If feature flag is off, all Phase 8 endpoints return 404.
- [ ] Fallback to text-based interview practice v2 must remain functional if realtime fails.
- [ ] Graceful disconnect: if WebRTC drops, session must be marked `aborted`, not `failed`.
- [ ] Reconnect option must be available within 5 minutes of disconnect.

---

## 9. Out-of-Scope (Explicitly Forbidden)

These are not part of Phase 8 and must not be implemented:

1. Emotion detection from voice/video.
2. Personality inference from voice/video.
3. Truthfulness detection from voice/video.
4. Age/gender/ethnicity inference from voice/video.
5. Hiring probability prediction.
6. Public sharing of raw audio/video.
7. Human recruiter scheduling.
8. Video/WebRTC between two human users.

---

## 10. Acceptance Criteria Checklist

| Rule | Description | Status |
|------|-------------|--------|
| G5-01 | No emotion/personality inference in feedback | ☐ |
| G5-02 | No truthfulness detection in feedback | ☐ |
| G5-03 | No protected attribute inference | ☐ |
| G5-04 | No hiring guarantee | ⏳ |
| G5-05 | Ephemeral token never logged | ⏳ |
| G5-06 | OpenAI API key never in frontend | ⏳ |
| G5-07 | Consent required before audio/camera | ⏳ |
| G5-08 | No raw transcript in analytics | ⏳ |
| G5-09 | No raw media in analytics | ⏳ |
| G5-10 | No raw media in logs | ⏳ |
| G5-11 | No media storage without consent | ⏳ |
| G5-12 | Disclaimer present in every feedback | ⏳ |
| G5-13 | Risk score not labeled truthfulness | ⏳ |
| G5-14 | Questions grounded in JD/CV evidence | ⏳ |
| G5-15 | Gap questions use "no evidence found" wording | ⏳ |
| G5-16 | Session scoped by user_id | ⏳ |
| G5-17 | Feature flag gates all Phase 8 routes | ⏳ |
| G5-18 | No CV text in analytics | ⏳ |
| G5-19 | No JD text in analytics | ⏳ |
| G5-20 | Learning tasks derive from analysis only | ⏳ |
