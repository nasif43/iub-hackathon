# 07 — Task Breakdown

Total budget: 4 hours. Suggested allocation is in `12_demo_plan.md` / execution order at the end of `agent.md`'s companion Next Steps (see final message). Tasks are written to be parallelizable across Backend / Frontend / Data / Testing lanes.

Every task below carries the required fields.

---
**T-01 — Data Loader**
- Objective: Load provided JSON/txt files into SQLite on startup.
- Description: Implement `backend/app/loader.py` reading `data/raw/company_standards.json` and all `C-00N.txt`, parsing the fixed header format (Contract ID / Title / Parties / Dataset Note), and upserting into `contracts` + `standards` tables per `04_database.md`.
- Inputs: files in `data/raw/`
- Outputs: populated `data/cra.db`
- Dependencies: `03_architecture.md`, `04_database.md`
- Acceptance Criteria: restarting the backend twice produces identical row counts (idempotent); all 8 contracts + 7 standards present.
- Estimated Difficulty: Low
- Estimated Time: 30 min
- Owner: Backend
- Files Allowed: `backend/app/loader.py`, `backend/app/db.py`
- Files Forbidden: frontend/, docs/

---
**T-02 — Clause Segmenter**
- Objective: Split each contract's raw text into (heading, body) blocks.
- Description: Regex on numbered headings (e.g. `^\d+\.\d+\s+.+$`) to split `raw_text` into ordered blocks, stopping at the "Dataset Note" line.
- Inputs: `contracts.raw_text`
- Outputs: list of `(heading, body)` tuples per contract
- Dependencies: T-01
- Acceptance Criteria: for all 8 sample contracts, block count matches the number of headed sections visible in the .txt files (verified by test).
- Estimated Difficulty: Medium
- Estimated Time: 40 min
- Owner: Backend
- Files Allowed: `backend/app/segmenter.py`, `backend/tests/test_classifier.py`
- Files Forbidden: frontend/

---
**T-03 — Clause Classifier**
- Objective: Map each (heading, body) block to one of the 7 fixed categories, or leave categories with no matching block as `present=0`.
- Description: Keyword-rule dictionary per category (config-driven, not hardcoded per contract) checked against heading first, falling back to body keywords if heading is ambiguous.
- Inputs: segmenter output
- Outputs: `clauses` rows
- Dependencies: T-02
- Acceptance Criteria: 100% correct category assignment on all 8 provided contracts (compare against the human-labeled headings in the .txt files).
- Estimated Difficulty: Medium
- Estimated Time: 40 min
- Owner: Backend
- Files Allowed: `backend/app/classifier.py`
- Files Forbidden: frontend/

---
**T-04 — Fact Extractor + Risk Rules**
- Objective: Extract numeric facts (days/months/%/hours) and apply deterministic per-category comparators.
- Description: Implement `facts.py` (regex → `{value, unit}` for numeric facts, plus a `payment_structure` shape per ADR-008 and a termination-grounds keyword check per ADR-009) and `risk_rules.py` (one function per category per `02_master_spec.md` risk-rule sketch, including the "sub-fact absent ≠ NEI" branch per ADR-010).
- Inputs: clause text + standard text
- Outputs: `risk_level`, structured facts used
- Dependencies: T-03, `company_standards.json`
- Acceptance Criteria: all 12 `public_test_questions.json` produce the expected risk direction; all 3 `missing_information_cases.json` produce NEI; **all 8 contracts C-001…C-008 pass explicit unit tests per category where applicable** (not just the 5 named in the original spec draft) — in particular: C-002/C-005/C-007 payment-structure handling, C-002 termination-grounds asymmetry, C-008 automatic-renewal magnitude escalation to High, C-007 IP as a Low-risk "don't over-flag a compliant clause" case, C-007 liability missing-carve-outs case, C-002/C-007/C-008 confidentiality missing-duration/missing-carve-outs cases.
- Estimated Difficulty: High
- Estimated Time: 60 min
- Owner: Backend
- Files Allowed: `backend/app/facts.py`, `backend/app/risk_rules.py`, `backend/tests/test_risk_rules.py`, `backend/tests/test_missing_information.py`
- Files Forbidden: frontend/

---
**T-05 — Explanation Builder**
- Objective: Produce the plain-language reason string.
- Description: Template-based sentence built from extracted facts (default path). Optional: if `USE_LLM_EXPLANATIONS=true`, call Anthropic API to rephrase, then verify the rephrase doesn't introduce new numbers/claims not present in the template version; discard and fall back to template if verification fails.
- Inputs: risk_level + facts + evidence text
- Outputs: `reason` string, `source` field (`rule_engine` or `rule_engine+llm`)
- Dependencies: T-04
- Acceptance Criteria: reason text never contains a number not present in either the contract evidence or standard text.
- Estimated Difficulty: Medium
- Estimated Time: 30 min
- Owner: Backend / AI Integration
- Files Allowed: `backend/app/explain.py`
- Files Forbidden: frontend/

---
**T-06 — API Layer**
- Objective: Implement all endpoints in `05_api.md`.
- Description: FastAPI routes wiring T-01…T-05 together plus `reviews` CRUD.
- Inputs: all above
- Outputs: running API on `localhost:8000` with `/docs` available
- Dependencies: T-01–T-05
- Acceptance Criteria: every endpoint in `05_api.md` returns the documented shape; Postman/curl smoke test passes for all 12 PQ + 3 MI cases.
- Estimated Difficulty: Medium
- Estimated Time: 40 min
- Owner: Backend
- Files Allowed: `backend/app/main.py`, `backend/app/models.py`, `backend/app/review.py`
- Files Forbidden: frontend/

---
**T-07 — Streamlit UI: Review Page**
- Objective: Implement Page 1 per `06_frontend.md`.
- Description: Contract picker, category tabs, Run Review button, Result Card, review actions.
- Inputs: API from T-06
- Outputs: working Streamlit page
- Dependencies: T-06 (can be stubbed/mocked earlier for parallel start)
- Acceptance Criteria: full happy-path and abstention-path demo flows from `06_frontend.md` work end to end.
- Estimated Difficulty: Medium
- Estimated Time: 50 min
- Owner: Frontend
- Files Allowed: `frontend/streamlit_app.py`
- Files Forbidden: backend/

---
**T-08 — Streamlit UI: Review History + About pages**
- Objective: Implement Pages 2 and 3.
- Dependencies: T-06
- Acceptance Criteria: history table renders and filters; About page shows safety disclaimer text.
- Estimated Difficulty: Low
- Estimated Time: 20 min
- Owner: Frontend
- Files Allowed: `frontend/streamlit_app.py`
- Files Forbidden: backend/

---
**T-09 — Test Suite: Public Questions + Missing Information**
- Objective: Automated pass/fail against the two provided test files.
- Description: Parse `public_test_questions.json` and `missing_information_cases.json`, hit the API for each, assert expected category/risk behavior.
- Dependencies: T-06
- Acceptance Criteria: all 15 cases green.
- Estimated Difficulty: Medium
- Estimated Time: 30 min
- Owner: Testing
- Files Allowed: `backend/tests/test_public_questions.py`, `backend/tests/test_missing_information.py`
- Files Forbidden: -

---
**T-10 — Demo Rehearsal + Script**
- Objective: Rehearse the exact click path in `12_demo_plan.md` at least twice.
- Dependencies: T-07, T-08, T-09 passing
- Acceptance Criteria: demo runs in under 5 minutes without live errors.
- Estimated Difficulty: Low
- Estimated Time: 20 min
- Owner: Presentation
- Files Allowed: `docs/12_demo_plan.md` (edits only)
- Files Forbidden: backend/, frontend/

---
**T-11 — README + Submission Checklist Pass**
- Objective: Final polish, `README.md`, run through `13_submission_checklist.md`.
- Dependencies: everything else
- Estimated Difficulty: Low
- Estimated Time: 15 min
- Owner: Documentation
- Files Allowed: `README.md`, `docs/13_submission_checklist.md`
