# AI CV Fit App — Phase 8 Team Plan

**Phase:** Phase 8  
**Feature:** Real-time AI Interview Simulator  
**Chosen direction:** Hướng A — OpenAI Realtime API qua WebRTC  
**Team:** Phúc — Quân — Đạt  
**Primary goal:** tạo một phòng phỏng vấn AI realtime có giọng nói, camera preview/recording tùy chọn, transcript, rubric feedback, interview summary và tích hợp với Target Jobs / Application Workspace / Learning Roadmap.

---

## 1. Phase 8 Executive Summary

Sau 7 phase, AI CV Fit App đã có:

- CV/JD analysis.
- Evidence-based scoring.
- Result dashboard.
- Application workspace.
- Target jobs.
- Learning roadmap.
- Interview practice text-based.
- Cover letter/application package.
- Usage/payment shell.
- Help assistant.
- Analytics/QA/deploy flow.

Phase 8 sẽ nâng cấp phần interview thành một feature demo mạnh:

```text
AI Interview Room
→ AI hỏi bằng giọng nói
→ user trả lời bằng microphone
→ transcript realtime
→ AI hỏi follow-up
→ hệ thống chấm rubric
→ cuối session có report
→ gợi ý learning tasks / next practice
```

Phase 8 không phải là một chatbot đơn giản. Đây là một **real-time multimodal interview simulation feature**.

---

## 2. Product Vision

Tên feature đề xuất:

```text
AI Interview Room
```

Product statement:

```text
AI Interview Room helps candidates practice realistic job interviews using real-time voice interaction, transcript-based feedback, evidence-aware scoring, and structured improvement reports tied to their target job and CV.
```

User value:

1. User luyện phỏng vấn như đang nói chuyện thật.
2. Câu hỏi bám JD/CV/application hiện có.
3. User được feedback sau từng câu hoặc cuối session.
4. Transcript giúp user xem lại câu trả lời.
5. Rubric giúp user biết yếu ở đâu.
6. Kết quả interview nối vào learning roadmap và application readiness.

---

## 3. Scope Decision

Team đã chọn:

```text
Hướng A — OpenAI Realtime API qua WebRTC
```

Điều này nghĩa là:

- frontend browser kết nối realtime bằng WebRTC,
- backend cấp ephemeral token,
- OpenAI API key không bao giờ nằm ở frontend,
- AI có thể nhận audio input và trả audio output,
- transcript/events được lưu lại để scoring và report.

---

## 4. Phase 8 Objectives

Phase 8 có 8 mục tiêu chính:

1. Xây `/interview/room` realtime interview UI.
2. Tạo session setup dựa trên target job/application.
3. Xin quyền microphone/camera rõ ràng.
4. Kết nối OpenAI Realtime API qua WebRTC bằng ephemeral token.
5. AI hỏi câu hỏi bằng voice.
6. User trả lời bằng voice, có live transcript.
7. Backend lưu session events/transcript/turns.
8. Cuối session tạo rubric report + next actions.

---

## 5. Must-have Features

Phase 8 bắt buộc có:

1. Interview room route.
2. Device permission screen.
3. Microphone required.
4. Camera preview optional.
5. Realtime session creation.
6. Ephemeral token endpoint.
7. WebRTC connection.
8. AI interviewer voice.
9. Live transcript panel.
10. Question/answer turn tracking.
11. End session button.
12. Final interview summary.
13. Rubric scoring.
14. Session history.
15. Privacy/consent copy.
16. Fallback if realtime connection fails.
17. Backend tests for ownership/token/session.
18. Manual browser QA.
19. Demo script.
20. Closeout report.

---

## 6. Should-have Features

Nếu đủ thời gian:

1. AI follow-up question based on weak answer.
2. Question type selector:
   - technical,
   - behavioral,
   - project deep-dive,
   - HR,
   - gap-check.
3. Difficulty selector:
   - easy,
   - medium,
   - hard.
4. Interview timer.
5. Per-question feedback.
6. Retry answer.
7. Speaking pace from transcript/audio timing.
8. Filler word count from transcript.
9. Integration with learning roadmap.
10. Export interview report.

---

## 7. Could-have Features

Nếu dư thời gian:

1. Optional full session video recording.
2. Interview playback.
3. Share interview summary, not raw recording.
4. Multiple interviewer personas.
5. Interview readiness trend over time.
6. Practice streak.
7. Session comparison.
8. Interview credits integration.
9. Admin/debug realtime event viewer.

---

## 8. Explicitly Out of Scope

Không làm trong Phase 8:

1. Emotion detection.
2. Personality inference.
3. Truthfulness detection.
4. Hiring probability prediction from face/voice.
5. Age/gender/ethnicity inference.
6. Full recruiter live interview portal.
7. Human interviewer scheduling.
8. Video/WebRTC between two human users.
9. Payment provider expansion.
10. Marketplace/job scraping.

Important rule:

```text
Video is optional and supportive.
Voice + transcript + rubric feedback is the core.
```

---

## 9. User Flow

### 9.1 Main Flow

```text
User logs in
→ opens target job/application
→ clicks “Start AI Interview”
→ chooses interview type and difficulty
→ sees consent + device check
→ allows microphone
→ optionally enables camera preview
→ backend creates interview session
→ backend returns ephemeral realtime token
→ frontend connects to OpenAI Realtime API via WebRTC
→ AI interviewer greets user and asks first question
→ user answers by voice
→ transcript appears
→ AI asks follow-up or next question
→ user completes interview
→ backend generates final rubric summary
→ user views interview report
→ user can create learning tasks from weak areas
```

### 9.2 Fallback Flow

If realtime connection fails:

```text
Realtime connection failed
→ app switches to recorded-answer fallback
→ user records answer
→ backend transcribes audio
→ backend scores answer
→ user still receives feedback
```

Fallback is not primary scope but should exist for demo safety.

### 9.3 Permission Denied Flow

If user denies microphone:

```text
Show clear message:
Microphone access is required for voice interview.
You can retry permission or switch to text practice.
```

If user denies camera:

```text
Continue with audio-only interview.
Camera is optional.
```

---

## 10. Technical Architecture

### 10.1 High-level Architecture

```text
Next.js Frontend
  - Interview room UI
  - WebRTC client
  - camera/mic permission
  - transcript panel
  - realtime event handling

FastAPI Backend
  - creates interview session
  - creates ephemeral token
  - stores session metadata
  - receives final transcript/events
  - generates rubric summary
  - stores report

OpenAI Realtime API
  - realtime voice interaction
  - speech in / speech out
  - live events/transcript

PostgreSQL
  - interview sessions
  - turns
  - transcripts
  - rubric reports

S3/local storage
  - optional audio/video artifacts
```

### 10.2 Realtime Connection Pattern

Recommended pattern:

```text
Frontend → Backend:
POST /v1/interview/realtime/sessions

Backend:
creates DB session

Frontend → Backend:
POST /v1/interview/realtime/sessions/{id}/client-secret

Backend → OpenAI:
creates ephemeral realtime client secret

Backend → Frontend:
returns ephemeral token only

Frontend → OpenAI Realtime:
connects via WebRTC using ephemeral token

Frontend/Backend:
stores transcript/events/summary
```

Security rule:

```text
OpenAI API key stays only on backend.
Frontend only receives short-lived ephemeral credential.
```

### 10.3 Proposed Backend Routes

```text
POST /v1/interview/realtime/sessions
GET /v1/interview/realtime/sessions
GET /v1/interview/realtime/sessions/{session_id}
POST /v1/interview/realtime/sessions/{session_id}/client-secret
POST /v1/interview/realtime/sessions/{session_id}/events
POST /v1/interview/realtime/sessions/{session_id}/complete
GET /v1/interview/realtime/sessions/{session_id}/summary
DELETE /v1/interview/realtime/sessions/{session_id}/media
```

Optional fallback:

```text
POST /v1/interview/realtime/sessions/{session_id}/answers/audio
```

### 10.4 Proposed Frontend Routes

```text
/interview/room
/interview/sessions
/interview/sessions/new
/interview/sessions/[id]/room
/interview/sessions/[id]/summary
/jobs/[id]/interview/realtime
/applications/[id]/interview/realtime
```

---

## 11. Data Model

### 11.1 interview_realtime_sessions

```text
id UUID primary key
user_id UUID not null
target_job_id UUID nullable
application_id UUID nullable
analysis_job_id UUID nullable
mode text not null              # realtime_voice | audio_fallback | video_optional
status text not null            # setup | active | completed | aborted | failed
interview_type text nullable    # technical | behavioral | project | hr | mixed
difficulty text nullable        # easy | medium | hard
consent_audio boolean default false
consent_camera boolean default false
consent_recording boolean default false
started_at timestamp nullable
ended_at timestamp nullable
created_at timestamp
updated_at timestamp
```

### 11.2 interview_realtime_turns

```text
id UUID primary key
session_id UUID not null
turn_index integer not null
question_text text
question_type text nullable
answer_transcript text nullable
ai_followup_text text nullable
started_at timestamp nullable
ended_at timestamp nullable
score_json json nullable
feedback_json json nullable
created_at timestamp
```

### 11.3 interview_realtime_events

```text
id UUID primary key
session_id UUID not null
event_type text not null
event_payload_json json nullable
redacted_payload_json json nullable
created_at timestamp
```

Store only safe/redacted event payloads.

### 11.4 interview_realtime_summaries

```text
id UUID primary key
session_id UUID not null
overall_score integer nullable
rubric_json json not null
strengths_json json nullable
weaknesses_json json nullable
suggested_improvements_json json nullable
next_questions_json json nullable
learning_tasks_json json nullable
created_at timestamp
updated_at timestamp
```

### 11.5 interview_media_artifacts

```text
id UUID primary key
session_id UUID not null
turn_id UUID nullable
artifact_type text not null       # audio_answer | video_recording | transcript
storage_key text nullable
duration_seconds integer nullable
mime_type text nullable
created_at timestamp
deleted_at timestamp nullable
```

For initial realtime mode, storing full audio/video is optional. Transcript storage is enough for MVP.

---

## 12. Realtime Session Configuration

The AI interviewer should be configured with:

```text
role: AI interview coach
context: target job, JD summary, CV evidence summary, missing gaps
rules:
- ask one question at a time
- do not ask sensitive personal questions
- do not infer protected attributes
- do not guarantee hiring outcome
- ask follow-up only based on user answer
- keep interview professional
- end after configured number of questions
```

Recommended session parameters:

```text
voice: choose one stable voice
turn_detection: server_vad if available
input_audio_transcription: enabled
instructions: interview-specific guardrails
modalities: audio + text
```

---

## 13. Interview Types

Support at least:

```text
technical
behavioral
project_deep_dive
hr
mixed
```

### Technical

Focus:

```text
skills required by JD
technical gaps
project evidence
tools/frameworks
```

### Behavioral

Focus:

```text
teamwork
challenge
learning ability
ownership
communication
```

### Project Deep-dive

Focus:

```text
CV projects
architecture
tradeoffs
impact
limitations
```

### HR

Focus:

```text
motivation
role fit
career goals
availability
salary expectation should be optional / not over-scored
```

### Mixed

Combination for demo.

---

## 14. Rubric

Each answer should be scored on:

```text
relevance
specificity
evidence
structure
technical_depth
communication_clarity
risk
```

Score range:

```text
0–100
```

Final summary:

```json
{
  "overall_score": 78,
  "rubric": {
    "relevance": 80,
    "specificity": 75,
    "evidence": 70,
    "structure": 82,
    "technical_depth": 74,
    "communication_clarity": 85,
    "risk": 20
  },
  "strengths": [],
  "weaknesses": [],
  "suggested_improvements": [],
  "next_practice_questions": [],
  "learning_tasks_to_create": []
}
```

Risk score means:

```text
higher risk = answer may be vague, unsupported, fabricated, or inconsistent with known evidence
```

Do not present risk as truthfulness detection.

---

## 15. Privacy and Safety Rules

### 15.1 Consent Required

Before interview starts, show:

```text
This interview room uses your microphone and may use your camera.
Audio is processed to generate transcripts and interview feedback.
Camera is optional.
Video recording is optional and disabled by default.
AI feedback is for practice only and does not guarantee hiring outcomes.
Do not share sensitive personal information during the interview.
```

User must confirm:

```text
I consent to microphone processing for interview practice.
```

Optional:

```text
I want to enable camera preview.
I want to record video for self-review.
```

### 15.2 Hard Rules

```text
No recording without explicit consent.
No raw audio/video in GA4.
No raw CV/JD/transcript in GA4.
No OpenAI API key in frontend.
Use ephemeral token/client secret only.
No emotion detection.
No personality inference.
No truthfulness detection.
No protected attribute inference.
No hiring guarantee.
No public sharing of audio/video by default.
Allow deleting media artifacts if stored.
```

### 15.3 Safe Feedback

Allowed:

```text
Your answer was clear but needs more specific project evidence.
You mentioned PostgreSQL, but did not explain your schema/design choices.
Try using STAR structure for behavioral answers.
Your answer was too short to assess technical depth.
```

Not allowed:

```text
You looked nervous.
You seem dishonest.
You have low confidence.
You are unlikely to be hired.
Your personality is not suitable.
```

---

## 16. Frontend Implementation Plan

### 16.1 Components

```text
InterviewSetupForm
DevicePermissionCheck
CameraPreview
MicrophoneMeter
RealtimeConnectionStatus
AIInterviewerPanel
TranscriptPanel
QuestionProgress
AnswerTimer
RubricFeedbackPanel
SessionControls
InterviewSummary
PermissionDeniedFallback
```

### 16.2 Frontend Pages

#### /interview/sessions/new

User selects:

```text
target job/application
interview type
difficulty
number of questions
camera on/off
recording consent
```

#### /interview/sessions/[id]/room

Main room:

```text
left: camera preview / AI interviewer avatar
center: current question / voice status
right: live transcript
bottom: controls
```

Controls:

```text
Start
Mute
Stop
End Session
Reconnect
Switch to fallback
```

#### /interview/sessions/[id]/summary

Show:

```text
overall score
rubric
question-by-question feedback
transcript
strengths
weaknesses
next practice questions
create learning tasks
add evidence to profile
```

---

## 17. Backend Implementation Plan

### 17.1 Services

```text
backend/app/services/interview_realtime/session_service.py
backend/app/services/interview_realtime/realtime_token_service.py
backend/app/services/interview_realtime/event_service.py
backend/app/services/interview_realtime/summary_service.py
backend/app/services/interview_realtime/rubric_service.py
backend/app/services/interview_realtime/media_service.py
```

### 17.2 Endpoint Responsibilities

#### Create session

```text
validate user
validate target job/application ownership
store session
return session id
```

#### Create client secret / ephemeral token

```text
validate session owner
create OpenAI realtime client secret
configure interview instructions
return ephemeral token
```

#### Store events

```text
validate session owner
redact unsafe payload
store safe event summary
```

#### Complete session

```text
validate owner
collect transcript/turns
generate rubric summary
store summary
return summary
```

---

## 18. Integration with Existing Product

### 18.1 Target Jobs

From job detail:

```text
Start AI Interview
```

Use job JD and attached analysis.

### 18.2 Application Workspace

From application:

```text
Practice interview for this application
```

Use application package, cover letter, result, learning gaps.

### 18.3 Learning Roadmap

Weak interview areas can create tasks:

```text
Practice explaining backend API design
Review FastAPI dependency injection
Prepare STAR story for teamwork
```

### 18.4 Career Profile

Good answers can suggest evidence items:

```text
Add this project explanation to profile evidence?
```

### 18.5 Usage / Billing

If credit gating exists:

```text
1 realtime interview session = 1 interview credit
or
1 answer feedback = 1 interview credit
```

Recommendation for MVP:

```text
Use soft gating first:
show usage but do not block interview room until stable.
```

---

## 19. Team Assignment

---

# 19.1 Phúc — Backend / Realtime / Architecture Lead

## Responsibilities

1. Realtime interview architecture.
2. API contracts.
3. DB models/migrations.
4. Interview session routes.
5. Ephemeral token endpoint.
6. OpenAI Realtime session configuration.
7. Transcript/event persistence.
8. Rubric scoring service.
9. Final summary generation.
10. Media storage policy.
11. Security/privacy implementation.
12. Render deploy/smoke.

## Files likely touched

```text
backend/app/api/routes/interview_realtime.py
backend/app/services/interview_realtime/
backend/app/services/media/
backend/app/db/models.py
backend/app/schemas/interview_realtime.py
backend/alembic/versions/
backend/tests/test_interview_realtime.py
docs/interview_realtime_api_contract.md
docs/interview_realtime_privacy.md
```

## Deliverables

1. API contract docs.
2. Session DB schema.
3. Realtime session endpoints.
4. Ephemeral token endpoint.
5. Summary endpoint.
6. Rubric scoring service.
7. Backend tests.
8. Smoke script/update.
9. Render deploy report.

## Acceptance Criteria

- OpenAI API key never exposed to frontend.
- Ephemeral token returned only to session owner.
- Session ownership enforced.
- Session can be started/completed.
- Transcript/turn data can be persisted.
- Final summary generated.
- Existing interview practice remains working.
- Backend tests pass.

---

# 19.2 Quân — Frontend / Interview Room UX Lead

## Responsibilities

1. Interview setup UI.
2. Device permission UI.
3. Camera preview.
4. Microphone meter.
5. WebRTC client integration.
6. AI interviewer UI.
7. Live transcript panel.
8. Session controls.
9. Summary page.
10. Fallback UI for permission/realtime failure.

## Files likely touched

```text
frontend/app/interview/sessions/new/
frontend/app/interview/sessions/[id]/room/
frontend/app/interview/sessions/[id]/summary/
frontend/components/interview-room/
frontend/lib/interviewRealtime.ts
frontend/lib/mediaDevices.ts
frontend/lib/api.ts
frontend/lib/types.ts
```

## Deliverables

1. `/interview/sessions/new`
2. `/interview/sessions/[id]/room`
3. `/interview/sessions/[id]/summary`
4. Device permission flow.
5. Camera preview.
6. Realtime connection UI.
7. Transcript panel.
8. End session flow.
9. Summary display.
10. Responsive polish.

## Acceptance Criteria

- User can grant/deny microphone.
- Camera can be enabled/disabled.
- Permission denied is handled.
- Realtime connection state visible.
- User can start/end interview.
- Transcript visible.
- Summary visible.
- UI does not leak token/client secret.
- Works in latest Chrome/Edge.

---

# 19.3 Đạt — QA / Privacy / Evaluation Lead

## Responsibilities

1. Privacy review.
2. Consent copy review.
3. Permission QA.
4. Browser compatibility checklist.
5. Realtime failure cases.
6. Rubric evaluation.
7. Guardrails.
8. E2E closeout report.
9. No raw media/PII analytics review.

## Files likely touched

```text
backend/tests/test_interview_realtime.py
backend/tests/test_interview_realtime_privacy.py
evaluation/cases/interview_realtime/
docs/interview_realtime_qa_checklist.md
docs/interview_realtime_guardrails.md
docs/interview_video_privacy_review.md
docs/interview_realtime_closeout_report.md
```

## Deliverables

1. QA checklist.
2. Privacy review.
3. Consent wording.
4. Rubric evaluation cases.
5. Backend privacy/access tests.
6. Manual browser QA.
7. Demo script.
8. Closeout audit.

## Acceptance Criteria

- No raw media in analytics.
- No raw transcript in GA4.
- Consent required before mic/camera.
- Permission denied handled.
- Realtime disconnect handled.
- Rubric does not overclaim.
- No emotion/personality/truthfulness inference.
- E2E demo pass.

---

## 20. PR Sequence

### PR 1 — Docs and API Contract

```text
docs/interview_realtime_product_plan.md
docs/interview_realtime_api_contract.md
docs/interview_realtime_privacy.md
docs/interview_rubric_contract.md
```

No code.

### PR 2 — Backend Session Foundation

```text
DB models
Alembic migration
session CRUD
ownership tests
summary placeholder
```

### PR 3 — Frontend Interview Room Skeleton

```text
/interview/sessions/new
/interview/sessions/[id]/room
device permission screen
camera preview
microphone meter
connection UI placeholder
```

### PR 4 — OpenAI Realtime WebRTC Integration

```text
backend ephemeral token endpoint
frontend WebRTC client
AI voice question
live transcript/events
disconnect handling
```

### PR 5 — Rubric Summary and Report

```text
turn tracking
transcript persistence
rubric scoring
summary endpoint
summary page
```

### PR 6 — Optional Video Layer

```text
camera preview polish
optional video recording
media artifact policy
delete media endpoint
privacy tests
```

### PR 7 — Product Integration

```text
target job integration
application workspace integration
learning task creation
usage/billing soft integration
```

### PR 8 — QA / Privacy / E2E Closeout

```text
browser QA
privacy review
guardrails
manual demo script
deployed smoke
closeout report
```

---

## 21. Roadmap Timeline

## Week 1 — Contract + Foundation

Phúc:

```text
API contract
DB schema
session endpoints
ephemeral token design
```

Quân:

```text
room skeleton
permission UI
camera/mic UI
```

Đạt:

```text
privacy doc
QA checklist
rubric contract review
```

Week 1 done:

```text
User can create an interview session and open room UI.
```

---

## Week 2 — Realtime Voice

Phúc:

```text
OpenAI realtime client secret endpoint
session instructions
event persistence
```

Quân:

```text
WebRTC client
AI voice output
user mic input
connection status
live transcript
```

Đạt:

```text
permission tests
realtime disconnect tests
no API key leak checks
```

Week 2 done:

```text
User can have a basic realtime voice interview.
```

---

## Week 3 — Scoring + Summary

Phúc:

```text
turn tracking
rubric scoring
summary endpoint
learning task suggestions
```

Quân:

```text
summary page
rubric cards
question-by-question feedback
```

Đạt:

```text
rubric evaluation cases
guardrail tests
manual QA
```

Week 3 done:

```text
Interview session produces a useful summary report.
```

---

## Week 4 — Video Optional + Product Integration + Closeout

Phúc:

```text
optional media storage/delete
target job/application integration
smoke/deploy
```

Quân:

```text
video preview/optional recording
final polish
responsive UI
```

Đạt:

```text
privacy review
browser QA
deployed E2E report
demo script
```

Week 4 done:

```text
Demo-ready realtime AI interview simulator.
```

---

## 22. Definition of Done

Phase 8 complete when:

1. User can create realtime interview session.
2. User can open interview room.
3. Microphone permission flow works.
4. Camera preview works as optional.
5. Backend issues ephemeral realtime token.
6. Frontend connects via WebRTC.
7. AI asks interview questions by voice.
8. User answers by voice.
9. Transcript is visible.
10. User can end session.
11. Session summary is generated.
12. Rubric scoring is shown.
13. Question-by-question feedback is shown.
14. Target job/application context is used.
15. No OpenAI API key in frontend.
16. No raw media in analytics.
17. Consent screen exists.
18. Permission denied is handled.
19. Disconnect/reconnect is handled.
20. Video feedback avoids sensitive inference.
21. Backend tests pass.
22. Manual browser QA pass.
23. Render/deployed smoke pass.
24. Demo script works.
25. Closeout report exists.

---

## 23. Demo Script

```text
1. Login as demo user.
2. Open Target Job detail.
3. Click Start AI Interview.
4. Choose Mixed interview, Medium difficulty, 5 questions.
5. Allow microphone.
6. Enable camera preview.
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

---

## 24. Key Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Realtime API latency | Demo feels bad | Keep answer turns short, show connection state |
| Browser permission denied | User blocked | Clear fallback and retry |
| API key leak | Critical | Backend ephemeral token only |
| Video privacy issue | Critical | Camera optional, no sensitive inference |
| Transcript quality poor | Feedback weak | Show editable transcript later if needed |
| Scope too big | Delay | Voice first, video optional |
| Render instability | Demo failure | Test deployed early |
| Cost spike | API cost | Limit session duration/questions |
| Rubric overclaim | Trust risk | Guardrails and wording |
| Analytics privacy leak | Privacy risk | No raw transcript/audio/video in GA4 |

---

## 25. Final Recommendation

Implement Phase 8 in this order:

```text
1. Realtime interview contract
2. Session foundation
3. Frontend room skeleton
4. WebRTC realtime voice
5. Transcript + summary
6. Optional video
7. Integration + QA closeout
```

Do not start with video analysis. The core demo value is:

```text
AI voice interviewer + user voice answer + transcript + rubric feedback + final report.
```
