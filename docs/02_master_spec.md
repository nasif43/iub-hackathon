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

> **Revision note (post spec-review, see ADR-008/009/010):** the first draft of this sketch was effectively derived from C-001/C-002/C-003/C-005/C-006 only. C-004, C-007, and C-008 each stress a gap the first draft didn't cover. All eight contracts are now named explicitly below so T-04 is tested against the full set, not five of eight.

- **Payment**: two distinct fact *shapes* can appear, and the extractor must handle both — treating the second shape as "no numeric days found → NEI" is a bug, not a valid abstention, because the clause is clearly present.
  - Shape A — `days_to_pay` vs. 30-day standard: `> 30` days favors Northstar-as-customer (Low Risk); a shorter deadline is a **higher risk to Northstar** as the payer. Concretely: **≥30 days → Low Risk; 15–29 days → Medium Risk; <15 days → High Risk** (C-001 = 15 days → Medium, at the boundary — confirm this exact cutoff in code, don't leave it implicit). Late fee > 1%/month → High Risk regardless of day count.
  - Shape B — `payment_structure` (no day count at all; prepayment or split-payment language): 100% due before work begins (C-002) → **High Risk** (full cash-flow exposure with zero leverage if work isn't delivered). Split payment e.g. 50/50 before-and-after acceptance (C-007) → **Medium Risk** (partial exposure, standard practice, but still front-loaded vs. the 30-days-after-acceptance standard). "Pay in full before campaign begins" (C-005) → **High Risk**, same reasoning as C-002.
  - Missing clause entirely → NEI.
- **Termination**: this category needs a **qualitative grounds check in addition to** the numeric notice-period check — day-counts alone miss the real risk.
  - Grounds asymmetry: if one party can terminate "for any reason" / "for convenience" with short notice while the other can only terminate for breach after a cure period (C-002: vendor 7 days any reason vs. customer 30-day cure-for-breach only) → **High Risk**, flagged explicitly as asymmetric rights, independent of the day-count comparison.
  - Notice-period-for-convenience directionality (symmetric case): compare against the 30-day standard. A **shorter** notice period than standard (e.g. C-005's 14 days) means Northstar gets **less stability/predictability** if the other party exits → Medium Risk. A **longer** notice period than standard (e.g. C-008's 90 days) means Northstar is **locked in longer** if it wants to exit → Medium Risk. Either direction away from 30 days is a deviation worth flagging; magnitude (>2x standard, as in C-008) pushes it toward High Risk rather than Medium.
  - Cure period vs. 10 business days: no cure right at all on a normal breach (C-006 — immediate termination, no right to fix) → **High Risk**, flagged explicitly.
  - Missing termination clause entirely (C-007) → NEI.
- **Automatic Renewal**: renewal length vs. ≤12 months; notice-to-cancel vs. ≤30 days. Both within standard → Low Risk. One dimension exceeds standard → Medium Risk (e.g. C-001: 12mo term is compliant but 60-day notice exceeds the 30-day standard). **Both** dimensions exceed standard, especially by ≥2x (C-008: 24mo term vs. ≤12mo, 90-day notice vs. ≤30-day — both roughly double) → **High Risk**; the magnitude cutoff is explicitly ≥2x standard on at least one dimension. No renewal clause present (C-004) → NEI, not Low Risk — absence of a clause is unknown/inapplicable, not automatically good (this is exactly MI-01).
- **Data Protection**: encryption at rest present? breach notice hours vs. ≤48h? subprocessor prior-approval required? deletion window vs. ≤30 days? Each missing/violated sub-point pushes risk up. C-003 fails nearly every sub-point (no encryption at rest, 72h breach notice, no subprocessor approval, 90-day deletion) → High Risk. C-006 meets or beats every sub-point → Low Risk. This category's rules are already fully worked and need no further examples.
- **Confidentiality**: duration vs. ≥3 years; carve-outs present (public/known/independent info); reciprocity (one-sided duty → at least Medium Risk, e.g. C-002, which also has no duration stated at all).
  - **Rule for a present-but-incomplete clause:** if the clause exists but a sub-fact (duration, carve-outs) is simply absent from the text, that is a risk signal on that sub-fact, **not** grounds to return NEI for the whole category — NEI is reserved for the clause type being entirely absent from the contract. C-002 (one-sided, no duration) → High Risk (asymmetry + missing duration compound).
  - **Missing carve-outs as its own risk contributor:** C-007 (1-year duration, no carve-outs mentioned) and C-008 (3-year duration, no carve-outs mentioned) both lack the public/known/independent-info exclusions the standard requires. C-007 also falls short on duration (1 year vs. ≥3 year standard) → High Risk. C-008 meets the duration bar but lacks carve-outs → Medium Risk.
- **Intellectual Property**: does customer own custom work after payment? is vendor's pre-existing IP properly licensed back? Vendor retaining all ownership with only a time-limited licence back (C-002: 6-month non-transferable licence; C-005: usable only while agreement is active) → High Risk. **C-007 is a fully standard-compliant clause** (customer owns post-payment deliverables, vendor keeps pre-existing tools, permanent licence back matches STD-IP-01 exactly) → **Low Risk** — this is a required "don't over-flag a compliant clause" test case, test it explicitly alongside the two High-risk examples.
- **Limitation of Liability**: cap window vs. 12 months of fees; carve-outs for fraud/gross negligence/confidentiality/DP/IP present? Shorter cap window (C-001: one month) → High Risk. Asymmetric liability (C-005: customer unlimited, vendor capped) → High Risk. **C-007 has a standard-matching 12-month cap but zero stated carve-outs** (no fraud/gross-negligence/DP/IP exclusions) → Medium Risk, same "missing carve-outs" pattern as Confidentiality above — test this explicitly, it's not in the two headline examples. Missing clause entirely (C-008) → NEI (this is MI-03).

> Exact thresholds above are now stated per-category, not left implicit. `07_tasks.md` T-04's acceptance criteria require all 8 contracts to pass, not a subset.

## Safety Rules (non-negotiable, enforced in code, checked in `11_review_checklist.md`)
1. No risk label without matching evidence text pulled verbatim from the source document (string containment check, not fuzzy match).
2. If a required clause type is absent from a contract → always `Not Enough Information`, never guessed.
3. If the LLM is enabled and its output can't be verified against source text → discard and use the rule-based template explanation instead; never surface unverified LLM text.
4. UI never uses the words "legal advice" to describe the tool's own output; a disclaimer is present on every screen.
5. `human_review` is always `"Required"` — there is no code path that omits it.

## In Scope vs Out of Scope
**In scope:** the workflow above, all 7 categories, SQLite-backed review/audit trail, Streamlit UI, FastAPI backend, static dataset.
**Out of scope:** OCR, file upload of arbitrary PDFs, auth, multi-tenant support, cloud deployment, CI/CD, monitoring, fine-tuning, real legal-advice generation.
