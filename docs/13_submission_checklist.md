# 13 — Submission Checklist

Directly maps to Problem Statement §8 "What You Need to Build."

- [ ] 1. A way to select a contract — Streamlit sidebar picker (T-07).
- [ ] 2. Support for at least 3 clause types — all 7 implemented (T-03, T-04).
- [ ] 3. Clause retrieval — Clause Segmenter + Classifier (T-02, T-03).
- [ ] 4. Company-standard retrieval — 1:1 category lookup (T-04, ADR-004).
- [ ] 5. Risk comparison — deterministic Risk Rules (T-04).
- [ ] 6. A risk level — one of the 4 fixed labels, always present (T-04, T-06).
- [ ] 7. A short explanation — Explanation Builder (T-05).
- [ ] 8. Evidence display — verbatim contract + standard text + standard ID, always shown together (T-06, T-07).
- [ ] 9. A human-review step — Approve/Reject/Mark/Feedback, persisted (T-06, T-07).
- [ ] 10. One missing-information example — MI-01/02/03, all three demonstrated (T-09, `12_demo_plan.md`).

## Explicitly confirm NOT built (per Problem Statement §10 — building these wastes time and isn't graded)
- [ ] No OCR / scanned-document handling.
- [ ] No model fine-tuning.
- [ ] No cloud infrastructure beyond local run.
- [ ] No authentication system.
- [ ] No CI/CD pipeline.
- [ ] No monitoring dashboard.
- [ ] No claim of giving legal advice anywhere in the product copy.

## Final pre-submission pass
- [ ] `11_review_checklist.md` fully checked off.
- [ ] `12_demo_plan.md` rehearsed at least twice, under 5 minutes.
- [ ] `README.md` at repo root explains how to run `backend/` and `frontend/` from a clean checkout in under 5 commands.
- [ ] `09_progress.md` and `10_handoffs.md` reflect the actual session history (not left as only the template examples).
