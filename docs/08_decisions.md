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
**ADR-007 — [Template for future decisions]**
- Context:
- Decision:
- Alternatives Considered:
- Consequences:
- Status: Proposed | Accepted | Superseded by ADR-XXX
