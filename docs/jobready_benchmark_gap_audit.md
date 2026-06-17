# JobReady-like Benchmark Gap Audit — AI CV Fit

> **Created:** 2026-06-17
> **Baseline commit:** `04ab4fa` (main; includes PR #60 polish, PR #61 GTM, PR #62 custom events)
> **Type:** Audit / planning only. No product code changes proposed in this doc.
> **Benchmark use:** JobReady-like product is a *functional/UX reference only*. Do not copy
> branding, assets, layout, names, colors, copy, or paid-flow mechanics.

---

## 1. Route inventory

| Route | Purpose | Auth | Backend dependency | Demo readiness | Notes |
|---|---|---|---|---|---|
| `/` | Landing | No | none | CLEAR | Redesigned in PR #58; hero CTA → `/login`. `landing_cta_click` fires. |
| `/login` | Login | No | `authApi.login` | CLEAR | `login_success` fires; redirects to `/dashboard`. |
| `/register` | Register | No | `authApi` | CLEAR | `RegisterForm` exists; no role split (candidate/recruiter). |
| `/dashboard` | CV/JD analysis + result | Yes | `jobApi` (upload, score, poll, result) | CLEAR | Core flow. Result renders in-place via `ResultCardV2`. `cv_analysis_*`, `result_view`, `download_report_click`. |
| `/history` | Past analyses | Yes | `jobApi` | PARTIAL | Exists; verify list + re-open + compare links on demo data. |
| `/applications` | Application list | Yes | `applicationsApi` | CLEAR | Empty state + "My Applications" copy (PR #60). |
| `/applications/new` | Create application | Yes | `applicationsApi.createApplication` | CLEAR | Posts `job_title` + `jd_text`. `application_create_success`. |
| `/applications/[id]` | Application detail/overview | Yes | `applicationsApi` | CLEAR | Hero + sub-nav (Package/Cover Letter/Interview/Evidence). `application_detail_view`. |
| `/applications/[id]/interview` | Interview practice | Yes | `interviewApi` | CLEAR (guarded) | Needs attached analysis. `interview_start`, `interview_answer_submit_success`. |
| `/applications/[id]/cover-letter` | Cover letter generate/edit | Yes | `coverLetterApi` | CLEAR (guarded) | `AnalysisRequiredBanner` when unattached. `cover_letter_generate_success` / `_save_success`. |
| `/applications/[id]/package` | Readiness package | Yes | `packageApi` | CLEAR (guarded) | Readiness mapped from `payload_json` (PR #60). `package_generate_success`. |
| `/profile` | Career profile | Yes | `profileApi` (degrades on 404) | PARTIAL | Thin; quick-link to Evidence Vault. |
| `/profile/evidence` | Evidence vault | Yes | `profileApi` CRUD | CLEAR | Skills/Projects/Achievements tabs. `profile_item_create_success`. |

**Missing routes (vs benchmark):** `/learning`, `/jobs` (marketplace), `/help`, `/pricing`/`/credits`, `/onboarding`, standalone interview-setup.

**App shell:** `PageShell` → top-nav `Header` (Dashboard / History / Applications / Profile + language toggle + logout). **No sidebar.** Active nav via `usePathname` (PR #60).

**Reusable assets already present (not yet surfaced as routes):**
`components/results/LearningRoadmap.jsx` (analysis-derived, takes `items[]`), `InterviewPrep.jsx`, `ImprovementPlan.jsx`, `SafeRewrite.jsx`, `EvidenceSection.jsx`, `ComparisonDashboard.jsx`. These are rendered inside the result dashboard today.

---

## 2. Current user journey map

| Step | Route/component | Status | Problem / cause | FE-only fix? | Backend needed? | Safe before demo? |
|---|---|---|---|---|---|---|
| Visitor landing | `/` `LandingPage` | CLEAR | — | — | No | Yes |
| Login/register | `/login`, `/register` | PARTIAL | No onboarding / role positioning | Yes | No | Yes |
| Dashboard / CV analysis | `/dashboard` | CLEAR | Long-running AI job (timing risk for live demo) | n/a | No | Yes (use panic path) |
| Result dashboard | `/dashboard` (`ResultCardV2`) | CLEAR | Result swaps in-place; fine | Yes | No | Yes |
| Create application | `/applications/new` | CLEAR | — | — | No | Yes |
| Attach/select analysis | `/applications/[id]` attach form | **CONFUSING** | User must **manually paste a Job ID** copied from dashboard | Partial (picker UI) | Ideal: list endpoint | Yes (pre-attach demo data) |
| Application detail | `/applications/[id]` | CLEAR | — | — | No | Yes |
| Interview practice | `…/interview` | CLEAR (guarded) | Empty until analysis attached + questions ready | Yes | No | Yes |
| Cover letter | `…/cover-letter` | CLEAR (guarded) | Generation latency | Yes | No | Yes |
| Package / readiness | `…/package` | CLEAR (guarded) | Generation latency | Yes | No | Yes |
| Profile/evidence | `/profile`, `/profile/evidence` | PARTIAL/CLEAR | `/profile` is thin | Yes | No | Yes |
| Analytics events | `lib/analytics.js` | CLEAR | Deployed + verified in GA4 Realtime | — | No | Yes |

**Strongest flow:** CV/JD analysis → result insight → application → interview → cover letter → package/readiness.
**Weakest/most confusing transition:** *create application → attach analysis* (manual Job ID paste).
**Biggest live-demo risk:** AI generation latency (analysis, package, cover letter) → mitigate with pre-seeded demo data + panic path.

---

## 3. Benchmark gap matrix (30 items)

Status: `COMPLETE / PARTIAL / MISSING / NOT_REQUIRED_FOR_DEMO / HIGH_RISK_TO_IMPLEMENT_NOW / PHASE_6_CANDIDATE`
Priority: `P0_DEMO_BLOCKER / P1_DEMO_IMPORTANT / P2_NICE_TO_HAVE / P3_PHASE_6 / DO_NOT_BUILD_NOW`
Risk: `LOW_FRONTEND_ONLY / MEDIUM_FRONTEND_PLUS_DATA / HIGH_BACKEND_OR_MIGRATION / HIGH_PRODUCT_RISK`

| # | Feature | Current state | Status | Priority | Risk | Backend dep | Suggested action | Phase |
|---|---|---|---|---|---|---|---|---|
| 1 | Landing clarity/trust | Redesigned, clear | COMPLETE | P2 | LOW | No | Minor copy polish | 5 |
| 2 | Register/login/onboarding | Works; no onboarding | PARTIAL | P1 | LOW | No | Add 1 onboarding hint/next-step | 5 |
| 3 | Candidate/recruiter positioning | None | MISSING | P2 | LOW | No | Position as candidate tool; defer recruiter | 6 |
| 4 | App shell/sidebar/nav | Top-nav, active state | PARTIAL | P1 | LOW | No | Keep top-nav; clarify flow breadcrumbs | 5 |
| 5 | Dashboard IA | Clear analysis-first | COMPLETE | P2 | LOW | No | — | 5 |
| 6 | CV upload/analyze | Works (upload+JD+settings) | COMPLETE | P0 | LOW | No | Ensure reachable in 1 click | 5 |
| 7 | Result dashboard/actionability | Rich (score, skills, plan) | COMPLETE | P0 | LOW | No | Strengthen "next step → application" CTA | 5 |
| 8 | Application workspace/tracking | List + detail + sub-nav | COMPLETE | P0 | LOW | No | — | 5 |
| 9 | Saved/target JD management | Application = JD holder | PARTIAL | P1 | LOW | No | Frame applications as "Target Jobs" | 5 |
| 10 | Full job marketplace/search | None | MISSING | P3 | HIGH_PRODUCT_RISK | Yes | Substitute: Target Jobs workspace | 6 |
| 11 | AI interview setup | Implicit (per application) | PARTIAL | P2 | LOW | No | Optional intro panel on interview page | 5/6 |
| 12 | AI interview practice room | Question list + answer + feedback | COMPLETE | P0 | LOW | No | No camera/video | 5 |
| 13 | Interview feedback/history | Rubric + answer history | COMPLETE | P1 | LOW | No | — | 5 |
| 14 | Cover letter generator | Generate + edit + save | COMPLETE | P0 | LOW | No | — | 5 |
| 15 | Application package/readiness | Readiness + skills + actions | COMPLETE | P0 | LOW | No | — | 5 |
| 16 | Profile/evidence vault | CRUD vault | COMPLETE | P1 | LOW | No | Enrich `/profile` summary | 5 |
| 17 | Learning/upskilling/roadmap | Component exists, no route | PARTIAL | P1 | LOW | No | Add `/learning` shell reusing `LearningRoadmap` | 5 |
| 18 | Help/chatbot/assistant | None | MISSING | P2 | LOW | No | Static guided FAQ drawer / `/help` | 5 |
| 19 | Pricing/credits visibility | None | MISSING | P3 | LOW | No | Static plan note (no payment) | 6 |
| 20 | Payment/checkout | None | NOT_REQUIRED_FOR_DEMO | DO_NOT_BUILD_NOW | HIGH_PRODUCT_RISK | Yes | Do not build | 6 |
| 21 | Analytics-ready funnel | 18 events live, GA4-verified | COMPLETE | P0 | LOW | No | Verify remaining events | 5 |
| 22 | Demo script & seed data | Partial (`phase5_demo_checklist.md`) | PARTIAL | P0 | LOW | No | Add demo script + panic path | 5 |
| 23 | Mobile/responsive polish | Mostly responsive | PARTIAL | P2 | LOW | No | Spot-check demo screens | 5 |
| 24 | Empty/loading/error states | Components exist, uneven | PARTIAL | P1 | LOW | No | Standardize across demo routes | 5 |
| 25 | i18n/copy consistency | EN/VI dict; some hardcoded VI | PARTIAL | P2 | LOW | No | Tidy demo-path copy | 5 |
| 26 | Accessibility basics | aria labels present | PARTIAL | P2 | LOW | No | Focus/labels on demo path | 5 |
| 27 | Performance/CWV | Next static; reasonable | PARTIAL | P2 | LOW | No | — | 5/6 |
| 28 | Security/privacy posture | Token auth, analytics allow-list | COMPLETE | P1 | LOW | No | Keep privacy boundary | 5 |
| 29 | Product story coherence | Strong core, gaps at edges | PARTIAL | P0 | LOW | No | PR A journey polish | 5 |
| 30 | Phase 6 scalability | n/a | PHASE_6_CANDIDATE | P3 | — | — | Roadmap doc | 6 |
