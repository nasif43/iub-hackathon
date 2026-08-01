# 01 — Requirements

## Functional Requirements

| ID | Requirement | Source | Acceptance Test |
|---|---|---|---|
| FR-01 | Load and list all 8 provided contracts by ID | Problem §5.1 | `GET /contracts` returns 8 items with id + title |
| FR-02 | Segment a contract's raw text into labeled clause blocks | Problem §5.2 | For C-001, system extracts 4 blocks: Payment, Termination, Automatic Renewal, Limitation of Liability |
| FR-03 | Classify each block into one of 7 fixed categories | Problem §4 | Classification matches the human-labeled headings in the .txt files 100% on the 8 provided contracts |
| FR-04 | Retrieve the correct company standard for a given category | Problem §5.3 | Category → standard is a direct 1:1 lookup (7 categories, 7 standards) |
| FR-05 | Compare contract clause against standard using extracted structured facts (numbers/periods), not free-text guessing | Problem §5.4 | PQ-02 (C-001 payment, 15 days vs. 30-day standard) yields a rule-derived verdict, not an LLM guess |
| FR-06 | Emit exactly one of 4 fixed risk labels per result | Problem §5.5 | No other string ever appears in the `risk_level` field |
| FR-07 | Produce a short plain-language explanation | Problem §5.6 | Explanation references the actual numbers/terms found, in ≤3 sentences |
| FR-08 | Show contract evidence + standard evidence + standard ID for every result | Problem §5.7 | Every API response includes `contract_evidence`, `standard_text`, `standard_id` |
| FR-09 | Return `Not Enough Information` when the relevant clause is absent from the contract, with no invented content | Problem §5.8 | MI-01, MI-02, MI-03 all produce NEI with a reason naming the missing clause type |
| FR-10 | Every result carries `human_review: "Required"` and supports Approve / Reject / Mark for review / Add feedback | Problem §5.9 | Reviewer actions persist to `reviews` table with a status and optional note |
| FR-11 | Support answering the 12 public test questions (PQ-01…PQ-12) | Participant Materials §6 | All 12 return the expected category/contract combination with correct risk direction |
| FR-12 | Support the 3 missing-information cases (MI-01…MI-03) | Participant Materials §8 | All 3 return NEI, never a guessed number |

## Non-Functional Requirements

| ID | Requirement | Rationale |
|---|---|---|
| NFR-01 | Build must be completable by a small team inside 4 hours | Contest duration |
| NFR-02 | No OCR, no file upload parsing beyond plain text | Explicitly out of scope |
| NFR-03 | No authentication/authorization system | Explicitly out of scope; add only a note in demo about future need |
| NFR-04 | No cloud infra beyond what's needed to run locally + demo | Explicitly out of scope |
| NFR-05 | Deterministic core: same input always yields same risk level | Judging criterion "prevents made-up answers" |
| NFR-06 | LLM usage (if any) must be optional/toggleable and never the source of the risk label | Anti-hallucination requirement |
| NFR-07 | All comparisons and standards must come only from the provided dataset | Rule #4 |
| NFR-08 | UI must visibly and unavoidably state "Human Review Required" on every result | Rule #6 |
| NFR-09 | System must never use the phrase "legal advice" in relation to its own output, and should carry a disclaimer | Rule #1 |

## Hidden Assumptions Made Explicit
- A1: The 3 mandatory categories are unknown until contest start → design must support all 7 (see ADR-006).
- A2: "Find important clauses" can be done reliably with heading/keyword matching because the provided contracts use consistent, clearly labeled section headers — no ML/NLP clause-boundary detection needed.
- A3: Standards map to categories 1:1 (7 standards, 7 categories) — no ambiguity in standard retrieval, so no vector search / RAG is needed.
- A4: "Compare the clause and standard" for numeric clauses (days, months, %, hours) can be reduced to numeric comparison rules; only qualitative clauses (e.g. IP ownership language, confidentiality scope) need any generative text, and even then evidence must be quoted verbatim.
- A5: Persistence only needs to survive the demo session — SQLite file is sufficient, no external DB.

## Missing Information (data gaps in the provided materials themselves)
- No specification of exact wording judges will use beyond PQ-01…PQ-12 — mitigated by keeping the classifier keyword-driven and easy to extend, not question-template-matched.
- No confirmed clause-type list for the "announced 3" — mitigated by A1.
- No API/auth requirement given by organizers — treat as none needed (NFR-03).
