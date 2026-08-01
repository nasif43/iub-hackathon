# 04 — Database Specification (SQLite, frozen)

Single file: `data/cra.db`. Created fresh from `data/raw/` at every backend startup (idempotent — drop and reseed is fine, this is a hackathon demo DB, not production data).

## Table: `contracts`
| Field | Type | Notes |
|---|---|---|
| id | TEXT PRIMARY KEY | e.g. `C-001` |
| title | TEXT | e.g. "BrightDesk SaaS Subscription Agreement" |
| parties | TEXT | free text, as given in source |
| raw_text | TEXT | full original .txt content |
| dataset_note | TEXT | the "Dataset Note" line, nullable |

## Table: `standards`
| Field | Type | Notes |
|---|---|---|
| id | TEXT PRIMARY KEY | e.g. `STD-PAY-01` |
| category | TEXT | one of the 7 fixed categories, UNIQUE |
| text | TEXT | verbatim standard text |

## Table: `clauses`
| Field | Type | Notes |
|---|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | |
| contract_id | TEXT | FK → contracts.id |
| category | TEXT | one of the 7 fixed categories |
| heading | TEXT | original heading text, nullable if inferred |
| text | TEXT | verbatim clause body |
| present | INTEGER (0/1) | 0 when category has no matching block in this contract |

Index: `idx_clauses_contract_category` on `(contract_id, category)` — this is the hot lookup path (used on every review request).

## Table: `reviews`
| Field | Type | Notes |
|---|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | |
| contract_id | TEXT | FK → contracts.id |
| category | TEXT | clause category reviewed |
| risk_level | TEXT | one of the 4 fixed labels |
| reason | TEXT | plain-language explanation shown to reviewer |
| contract_evidence | TEXT | verbatim clause text, nullable if NEI with no clause |
| standard_id | TEXT | FK → standards.id, nullable if NEI |
| standard_text | TEXT | verbatim standard text, nullable if NEI |
| source | TEXT | `"rule_engine"` or `"rule_engine+llm"` — audit trail of how the explanation was produced |
| status | TEXT | `pending` \| `approved` \| `rejected` \| `marked_for_review`, default `pending` |
| reviewer_note | TEXT | free text, nullable |
| created_at | TEXT | ISO timestamp |
| updated_at | TEXT | ISO timestamp |

Index: `idx_reviews_contract` on `(contract_id)`.

## Constraints (enforced in application code, SQLite has no CHECK needed but add if trivial)
- `risk_level` ∈ {`Low Risk`, `Medium Risk`, `High Risk`, `Not Enough Information`}
- `status` ∈ {`pending`, `approved`, `rejected`, `marked_for_review`}
- If `risk_level = 'Not Enough Information'` then `contract_evidence` may be NULL, but `reason` must explicitly name the missing category (e.g. "No automatic renewal clause found in this contract excerpt").
- Every row in `reviews` must have non-null `standard_id`/`standard_text` UNLESS `risk_level = 'Not Enough Information'`.

## Seeding logic (loader.py responsibility, described here for schema clarity)
1. Parse `company_standards.json` → insert into `standards` (7 rows, category is UNIQUE key so re-seeding is idempotent via upsert).
2. For each `C-00N.txt` → parse header (Contract ID, Title, Parties), Dataset Note, and run Clause Segmenter/Classifier → insert one `contracts` row + one `clauses` row per detected category (7 categories checked per contract; categories with no match get `present=0` and empty `text`).
