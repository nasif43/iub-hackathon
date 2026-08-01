# 02 — Master Spec (Single Source of Truth)

If any other document disagrees with this one, **this document wins** unless overridden by a dated entry in `08_decisions.md`.

## System name
Contract Review Assistant (CRA) — internal hackathon codename, no branding needed.

## Core Principle (read this before writing any code)
> **The risk label is never decided by an LLM.** It is decided by deterministic comparison rules operating on facts extracted from the contract text and the fixed company-standard text. An LLM, if used at all, is only permitted to (a) help extract a number/period from oddly-phrased text, with its output validated against the source string, or (b) phrase the final explanation sentence, with its output checked to ensure it doesn't introduce any fact not present in the evidence. If the LLM's output can't be verified, fall back to a template-based explanation. This is the answer to "how do you prevent made-up answers."

## End-to-End Workflow (maps 1:1 to Problem Statement §3)
1. **Select a contract** — user picks one of C-001…C-008 from a list.
2. **Find important clauses** — Clause Segmenter splits raw text into headed blocks; Clause Classifier tags each block with one of the 7 categories (or leaves categories absent if no block matches).
3. **Find the matching company standard** — direct category → standard lookup from `company_standards.json`.
4. **Compare both texts** — Fact Extractor pulls structured values (days, months, %, hours) from both texts; Risk Comparator applies category-specific rules.
5. **Show the risk level** — one of the 4 fixed labels.
6. **Explain the reason** — short, plain-language, references the actual extracted numbers/terms.
7. **Show the evidence** — verbatim contract clause, verbatim standard text, standard ID.
8. **Send for human review** — result is written to `reviews` table as `pending`; reviewer can Approve / Reject / Mark for review / Add feedback.

## Fixed Vocabulary
- Clause categories (7): `Payment`, `Termination`, `Data Protection`, `Confidentiality`, `Automatic Renewal`, `Intellectual Property`, `Limitation of Liability`
- Risk levels (4): `Low Risk`, `Medium Risk`, `High Risk`, `Not Enough Information`
- Review decisions (4): `approved`, `rejected`, `marked_for_review`, `feedback_added` (feedback can co-occur with any status)

## Category → Standard mapping (frozen, from `company_standards.json`)
| Category | Standard ID |
|---|---|
| Payment | STD-PAY-01 |
| Termination | STD-TERM-01 |
| Data Protection | STD-DP-01 |
| Confidentiality | STD-CONF-01 |
| Automatic Renewal | STD-REN-01 |
| Intellectual Property | STD-IP-01 |
| Limitation of Liability | STD-LIAB-01 |

## Risk Rule Sketch (deterministic; full rules live in code as config, this is the spec)
- **Payment**: contract days-to-pay vs. 30-day standard. `> 30` days favors the company (Low Risk, better than standard). Fewer days than 30 is *worse for the customer paying* — but note Northstar is the customer in most contracts, so a *shorter* deadline (e.g., 15 or 7 days) is a **higher risk to Northstar** as the paying party. Late fee > 1%/month → High Risk. Missing clause → NEI.
- **Termination**: notice period vs. 30 days; cure period vs. 10 business days; asymmetric rights (one party gets more than the other) → at least Medium Risk. Immediate termination with no cure right → High Risk (flag explicitly, e.g. C-006). Missing clause → NEI.
- **Automatic Renewal**: renewal length vs. ≤12 months; notice-to-cancel vs. ≤30 days. Both within standard → Low Risk. Either exceeds standard → Medium/High depending on magnitude. No renewal clause present → NEI (not "Low Risk" — absence of a clause is not automatically good, it's unknown/inapplicable per MI-01).
- **Data Protection**: encryption at rest present? breach notice hours vs. ≤48h? subprocessor prior-approval required? deletion window vs. ≤30 days? Each missing/violated sub-point pushes risk up; e.g. "encryption of stored data is not required" (C-003) → High Risk.
- **Confidentiality**: duration vs. ≥3 years; carve-outs present (public/known/independent info); reciprocity (one-sided duty → Medium/High, e.g. C-002).
- **Intellectual Property**: does customer own custom work after payment? is vendor's pre-existing IP properly licensed back? Vendor retaining all ownership with only a time-limited licence back (e.g. C-002, C-005) → High Risk.
- **Limitation of Liability**: cap window vs. 12 months of fees; carve-outs for fraud/gross negligence/confidentiality/DP/IP present? Shorter cap window (e.g. C-001's "one month") → High Risk. Asymmetric liability (customer unlimited, vendor capped, e.g. C-005) → High Risk. Missing clause → NEI.

> Exact thresholds and edge cases are enumerated per-category in code comments, seeded from the 8 sample contracts, so `07_tasks.md` T-04 can implement this without re-deriving it from scratch.

## Safety Rules (non-negotiable, enforced in code, checked in `11_review_checklist.md`)
1. No risk label without matching evidence text pulled verbatim from the source document (string containment check, not fuzzy match).
2. If a required clause type is absent from a contract → always `Not Enough Information`, never guessed.
3. If the LLM is enabled and its output can't be verified against source text → discard and use the rule-based template explanation instead; never surface unverified LLM text.
4. UI never uses the words "legal advice" to describe the tool's own output; a disclaimer is present on every screen.
5. `human_review` is always `"Required"` — there is no code path that omits it.

## In Scope vs Out of Scope
**In scope:** the workflow above, all 7 categories, SQLite-backed review/audit trail, Streamlit UI, FastAPI backend, static dataset.
**Out of scope:** OCR, file upload of arbitrary PDFs, auth, multi-tenant support, cloud deployment, CI/CD, monitoring, fine-tuning, real legal-advice generation.
