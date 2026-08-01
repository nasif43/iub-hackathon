# 11 — Review Checklist (Rule-by-Rule Compliance)

Run through this before any demo or submission. Maps directly to Problem Statement §12 "Important Rules" and Participant Materials §10 "Participant Checklist."

## Problem Statement §12 — Important Rules
- [ ] Rule 1 — System never claims to give legal advice (check UI copy + About page).
- [ ] Rule 2 — No made-up clauses or legal rules anywhere in the output (spot-check against source .txt files for every demo case).
- [ ] Rule 3 — Every risk result shows evidence (contract text + standard text + standard ID); no bare risk label ever shown.
- [ ] Rule 4 — Only the 8 provided contracts and 7 provided standards are used; no external legal knowledge injected into the comparison logic.
- [ ] Rule 5 — Uncertain results are clearly marked `Not Enough Information`, never silently guessed.
- [ ] Rule 6 — A human reviewer is always the final decision-maker; "Human Review: Required" appears on every single result with no exceptions.

## Participant Materials §10 — Participant Checklist
- [ ] Supports at least 3 announced clause categories (in practice: all 7 are supported).
- [ ] Every risk result includes exact contract evidence (verbatim substring check).
- [ ] Every comparison includes the correct standard and standard ID.
- [ ] System returns `Not Enough Information` when a clause is missing.
- [ ] Interface clearly shows human review is required.
- [ ] Team can explain how the solution could be secured and scaled later (see `12_demo_plan.md` talking points).

## Mandatory Test Cases (must pass before demo)
- [ ] PQ-01 … PQ-12 all return the expected contract/category and a defensible risk direction.
- [ ] MI-01 (C-004, automatic renewal) → `Not Enough Information`, explanation names the missing clause, no invented notice period.
- [ ] MI-02 (C-007, termination for convenience) → `Not Enough Information`, no invented termination terms.
- [ ] MI-03 (C-008, liability cap) → `Not Enough Information`, no invented cap figure.

## Additional Test Cases (added after spec review — non-headline contracts the original draft missed)
- [ ] C-002 Payment (100% prepaid) → High Risk via `payment_structure` shape, not NEI (ADR-008).
- [ ] C-005 Payment (paid before campaign begins) → High Risk, same shape.
- [ ] C-007 Payment (50/50 split) → Medium Risk, same shape.
- [ ] C-002 Termination → High Risk flagged specifically as grounds asymmetry (any-reason/7-day vs. breach-only/30-day cure), not just a day-count diff (ADR-009).
- [ ] C-008 Automatic Renewal → escalates to High Risk (both dimensions ≥2x standard), not stuck at Medium.
- [ ] C-002 Confidentiality → High Risk; missing duration is scored as a risk contributor, not a category-wide NEI (ADR-010).
- [ ] C-007 Confidentiality → High Risk (short duration + missing carve-outs).
- [ ] C-008 Confidentiality → Medium Risk (duration compliant, carve-outs missing).
- [ ] C-007 Intellectual Property → **Low Risk** (fully standard-compliant clause — confirms the system doesn't over-flag a good clause).
- [ ] C-007 Limitation of Liability → Medium Risk (compliant cap window, missing carve-outs).

## Anti-Hallucination Spot Checks
- [ ] Every `contract_evidence` string is an exact substring of the source `.txt` file (automate this as a test assertion, not a manual check).
- [ ] Every `standard_text` string matches `company_standards.json` verbatim.
- [ ] If `USE_LLM_EXPLANATIONS=true`, confirm the fallback-to-template path actually triggers when a test forces an unverifiable LLM response (write one deliberate failure test for this).
