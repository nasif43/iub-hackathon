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

## Anti-Hallucination Spot Checks
- [ ] Every `contract_evidence` string is an exact substring of the source `.txt` file (automate this as a test assertion, not a manual check).
- [ ] Every `standard_text` string matches `company_standards.json` verbatim.
- [ ] If `USE_LLM_EXPLANATIONS=true`, confirm the fallback-to-template path actually triggers when a test forces an unverifiable LLM response (write one deliberate failure test for this).
