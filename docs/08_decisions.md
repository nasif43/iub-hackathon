# 08 — Architecture Decision Records

Every major decision, dated and numbered. Never silently override one — add a new ADR that supersedes it.

---
**ADR-001 — Risk level is computed by deterministic rules, not by an LLM**
- Context: Judging criterion explicitly asks how the team prevents made-up answers. LLM-only comparison risks hallucinated risk levels and fabricated evidence.
- Decision: Risk labels come from rule-based comparators over regex-extracted facts. LLM (if used) is confined to explanation phrasing and its output is verified against source text before display.
- Alternatives Considered: Pure LLM/RAG comparison (rejected — unverifiable, non-deterministic); vector search over clauses (rejected — overkill for 8 short, clean contracts with 1:1 category-standard mapping).
- Consequences: Slightly more upfront engineering per category, but fully explainable and demo-safe.
- Status: Accepted

---
**ADR-002 — Streamlit over a JS frontend framework**
- Context: 4-hour budget, need for reliability and demo speed.
- Decision: Streamlit single-page app.
- Alternatives Considered: React/Next.js (rejected — build pipeline risk under time pressure); plain Flask+Jinja (rejected — more boilerplate than Streamlit for the same result).
- Consequences: Less visual polish than a custom React UI, but far lower risk of a broken build minutes before demo.
- Status: Accepted

---
**ADR-003 — SQLite instead of no database**
- Context: Requirement to keep a human in the process with Approve/Reject/Mark/Feedback actions implies some persistence beyond the demo session, and judges may ask to see an audit trail.
- Decision: Single-file SQLite, reseeded from source data on each backend start.
- Alternatives Considered: In-memory only (rejected — Review History page and audit trail would vanish on refresh, weakens the "human in the loop" story); Postgres (rejected — unnecessary infra for a 4-hour local demo).
- Status: Accepted

---
**ADR-004 — Category-to-standard mapping is a static 1:1 dictionary, not vector/semantic search**
- Context: `company_standards.json` has exactly 7 standards, each with a `category` field matching one of the 7 required clause categories exactly.
- Decision: Direct dictionary lookup.
- Alternatives Considered: Embedding-based retrieval (rejected — adds a dependency, latency, and a new failure mode for zero benefit given a 1:1, already-labeled mapping).
- Status: Accepted

---
**ADR-005 — LLM usage is optional and off by default (`USE_LLM_EXPLANATIONS=false`)**
- Context: Team should be able to demo with zero external API dependency in case of network issues at the venue, and the LLM must never be a single point of failure for the "no made-up answers" story.
- Decision: Ship a working template-based explanation path first; LLM rewrite is an enhancement layer, verified before use, with automatic fallback.
- Status: Accepted

---
**ADR-006 — Support all 7 clause categories rather than pre-committing to 3**
- Context: Organizers announce the mandatory 3 categories only at contest start; which 3 is unknown at doc-writing time.
- Decision: Build the classifier/risk-rule engine as config-driven across all 7 categories so any announced subset of 3 works without a code change.
- Alternatives Considered: Guessing the 3 most likely categories and hardcoding those only (rejected — high risk of guessing wrong and needing an emergency rebuild under time pressure).
- Status: Accepted

---
**ADR-008 — Payment category needs two fact shapes, not one**
- Context: Intelligence-layer spec review (Groq/OpenRouter-run reviewer, dated during T-04 prep) found that C-002, C-005, and C-007 express payment terms as prepayment/split-payment structures with no "days after invoice" figure at all. A pure day-count regex either finds nothing (mis-firing as NEI on a clause that's clearly present) or crashes.
- Decision: Fact Extractor emits one of two shapes for Payment: `days_to_pay` (numeric) or `payment_structure` (prepayment %, split schedule). Risk Comparator has a branch for each; see `02_master_spec.md`.
- Alternatives Considered: Force everything into a day-count (rejected — C-002's "100% before work begins" has no day count to force); silently NEI on no day-count found (rejected — this is exactly the "invent an abstention where a real clause exists" failure mode the project is built to avoid).
- Consequences: Fact Extractor and Risk Comparator both need a shape-detection step for Payment specifically; other categories don't need this.
- Status: Accepted

---
**ADR-009 — Termination needs a qualitative grounds check, not only numeric notice/cure comparison**
- Context: Spec review flagged that C-002's asymmetry (vendor: any-reason/7-day notice; customer: breach-only/30-day cure) is a difference in termination *grounds*, invisible to a comparator that only diffs day-counts.
- Decision: Risk Comparator for Termination checks each party's stated grounds (keyword match on "for any reason" / "for convenience" vs. "for breach" / "material breach") in addition to comparing notice/cure day-counts.
- Status: Accepted

---
**ADR-010 — "Clause present but a sub-fact is missing" is a risk signal, not a category-wide abstention**
- Context: Spec review found this pattern in two categories independently — C-002's Confidentiality clause has no stated duration, and C-007/C-008's Confidentiality and C-007's Limitation of Liability clauses lack carve-out language — and the original rule sketch had no rule for it, risking an incorrect NEI on a clause that plainly exists.
- Decision: NEI is reserved strictly for "this clause type does not appear anywhere in the contract." If the clause type is present but a specific sub-fact (duration, carve-outs) is absent from its text, that absence is scored as a risk contributor within Low/Medium/High, never as NEI.
- Consequences: Risk Comparator functions need a "sub-fact absent" branch distinct from the "category absent" branch that triggers NEI — these must not share code paths.
- Status: Accepted

---
**ADR-011 — LLM explanation layer runs on Groq / OpenRouter, not Anthropic API**
- Context: Team decision to avoid any paid Anthropic API usage for this build.
- Decision: `USE_LLM_EXPLANATIONS`, when enabled, calls Groq or OpenRouter instead of the Anthropic API referenced in the original architecture draft. All references to `ANTHROPIC_API_KEY` / `claude-sonnet-4-6` in `03_architecture.md` and `.env.example` are replaced with the equivalent Groq/OpenRouter env vars and model string.
- Consequences: The verification-before-display rule (ADR-001) is provider-agnostic and still applies in full — whichever provider's response comes back still gets checked against source evidence before being shown, with the same discard-and-fall-back-to-template behavior on failure. No change to the core anti-hallucination architecture, only to which API sits behind the optional explanation-rewrite step.
- Status: Accepted (supersedes the Anthropic-specific env vars in `03_architecture.md`)

---
**ADR-013 — OpenRouter LLM Fallback for Fact Extraction (`USE_LLM_FACT_EXTRACTION`)**
- Context: Clauses with complex or non-standard numeric phrasings (e.g. text numbers, uncommon units) may fail regex and unit conversion.
- Decision: Introduce `USE_LLM_FACT_EXTRACTION` (default `false`). When enabled and `OPENROUTER_API_KEY` is present, if standard regex/unit-conversion finds no numeric match for a present clause, query OpenRouter for a structured `{value, unit}` pair. The extracted numeric value MUST pass a strict verbatim string containment check against the source clause text before being used. Results are cached and tagged with source `"rule_engine+llm_extraction"`.
- Consequences: Ensures zero hallucinated numbers reach the risk comparator while supporting complex text phrasings when enabled. Defaults to false for zero-external-dependency offline execution.
- Status: Accepted
