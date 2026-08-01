# 00 — Problem Statement (Extracted)

Source documents: `IUBPC_Hackathon_Problem_Statement.pdf`, `IUBPC_Participant_Materials.pdf`.
This file is the canonical restatement. If any other doc conflicts with this one, this one wins unless `08_decisions.md` records an override.

## Event
- Intra IUB Hackathon, Final Round
- Duration: 4 hours
- Deliverable: a working prototype (not a pitch deck, not a mockup)

## One-line goal
Build a small, complete, safe AI system that helps a human reviewer check contract clauses against company-approved standards, show evidence, flag risk, and abstain safely when information is missing.

## Objectives
1. Read a provided contract (plain text, already clean — no OCR/parsing needed).
2. Find clauses belonging to at least 3 of 7 required categories.
3. Retrieve the matching company standard for each clause category.
4. Compare contract clause vs. standard.
5. Emit one of exactly four risk labels.
6. Explain the reasoning in plain language.
7. Show evidence (exact contract text + exact standard text + standard ID).
8. Route every result into a human-review step (Approve / Reject / Mark for review / Add feedback).

## Required clause categories (7 total; ≥3 must be supported; organizers announce which 3 are mandatory day-of)
Payment · Termination · Data Protection · Confidentiality · Automatic Renewal · Intellectual Property · Limitation of Liability

> **Assumption (see 08_decisions.md ADR-006):** Since the mandatory 3 are announced at contest start and we can't know them now, the system must support **all 7** categories out of the box so any 3-subset works without code changes.

## Risk labels (fixed vocabulary — no others allowed)
`Low Risk` · `Medium Risk` · `High Risk` · `Not Enough Information`

## Required output fields (from Participant Materials §2)
1. Contract ID and clause type
2. Risk level
3. Exact contract clause (evidence)
4. Matching company standard + standard ID
5. Short explanation of the difference
6. `Human Review: Required` (always present, always required — never optional)

## Hard constraints / non-negotiable rules (Problem Statement §12)
1. Never claim to give legal advice.
2. Never invent a clause, rule, or legal explanation.
3. Every risk result must show evidence.
4. Use only the provided/approved information (8 contracts + `company_standards.json`) — no outside legal knowledge injected.
5. Mark uncertain results clearly (`Not Enough Information`).
6. A human always makes the final decision — the system never "decides."

## Explicitly out of scope (Problem Statement §10)
Full legal platform, model fine-tuning, large-scale cloud infra, real auth/security systems, CI/CD pipelines, monitoring dashboards, OCR, legal-advice generation.

## Provided data assets
- `company_standards.json` — 7 standards (STD-PAY-01, STD-TERM-01, STD-DP-01, STD-CONF-01, STD-REN-01, STD-IP-01, STD-LIAB-01)
- `C-001.txt` … `C-008.txt` — 8 contract excerpts, each with clearly labeled headings (e.g. "2.1 Payment") and a "Dataset Note" stating what's deliberately missing
- `public_test_questions.json` — 12 dev-time test questions (PQ-01…PQ-12)
- `missing_information_cases.json` — 3 abstention test cases (MI-01…MI-03), all requiring `Not Enough Information`

## Judging / presentation criteria (Problem Statement §9)
Teams must be able to explain, live:
- How the system works end to end
- How it finds the correct clause
- How it compares clause vs. standard
- **How it prevents made-up answers** ← this is the one most teams will fumble; our answer is the deterministic-rules-first architecture in `03_architecture.md`
- How it would scale to more contracts
- How private contracts could be protected
- What they'd improve with more time

## Risks to this team's execution (not risks in the contracts)
| Risk | Mitigation |
|---|---|
| Over-scoping to all 7 categories burns the 4-hour budget | Build the rule engine generically once (category-driven config), not 7 bespoke code paths |
| LLM hallucinates a risk level or invents a clause | LLM is never the source of the risk label; if used at all, its output text is verified as a substring of source data before display |
| Team spends time on auth/infra that isn't graded | Explicitly forbidden in `13_submission_checklist.md` — do not build it |
| Missing-information cases get "cleverly" answered instead of abstained | `MI-01/02/03` are hard-coded as required test cases in `11_review_checklist.md`; any answer to them other than NEI is a failing build |
