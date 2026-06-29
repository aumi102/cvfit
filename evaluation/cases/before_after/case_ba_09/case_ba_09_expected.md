# Expected Behavior — Before/After Case 09: Keyword Stuffing with Unrelated Tech

## Category
Keyword stuffing — many irrelevant skills added without evidence

## CV Summary (Base)
CV has relevant backend skills (FastAPI, PostgreSQL, Redis, Docker) but no Kubernetes or AWS. Gaps exist but evidence for existing skills is decent.

## CV Summary (Revised)
Revised CV adds Kubernetes, AWS to skills list — these are relevant. BUT it ALSO adds an extensive list of completely unrelated technologies (Terraform, Prometheus, Grafana, ElasticSearch, MongoDB, RabbitMQ, GraphQL, gRPC, WebSockets, Rust, Go, Machine Learning, AI, Blockchain) with NO project evidence. This is classic keyword stuffing.

## Expected Comparison Result
- base_score: 55–68 (partial — good core but missing Kubernetes, AWS, testing)
- new_score: 58–72 (slight improvement — Kubernetes/AWS added but rest is stuffing)
- score_delta: +3 to +15 (NOT a dramatic improvement — keyword stuffing should be penalized)
- resolved_missing_skills: Kubernetes, AWS (listed but evidence still thin)
- still_missing_skills: Testing, deep Kubernetes, deep AWS
- keyword_stuffing_warnings: MUST fire for ML/AI/Blockchain/Rust/Go/GraphQL/gRPC (irrelevant to backend engineer JD, no evidence)
- improvement_summary: should note keyword stuffing with irrelevant technologies

## Score Components Expected
- Small delta — keyword stuffing should NOT result in large score improvement
- keyword stuffing detection MUST fire for irrelevant technologies

## Guardrail Checks
- keyword_stuffing_warnings MUST contain warnings for the irrelevant technologies
- improvement_summary must NOT praise the CV for adding ML/AI/Blockchain
- score_delta should be small despite the long skills list
