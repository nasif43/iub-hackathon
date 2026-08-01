# 14 — Next Steps: Prompts for Each Tool

**Role split (per team preference):** browser-based chat AIs are used only as an *intelligence layer* — planning review, risk-rule sanity-checking, explanation-quality review, presentation coaching. They do not write or touch code. All code is implemented by CLI/IDE-based coding agents working directly in the repo.

- **Intelligence layer only (no code output accepted from these):** Claude.ai / ChatGPT / Gemini (web)
- **Implementation agents (work directly in the repo):** Claude Code, Antigravity IDE, Agy CLI, Opencode

Every prompt below is self-contained and references only files in this repo — no prior chat history required.

---

## Prompt for Claude (web) / Gemini (web) — intelligence layer, review only
```
You are reviewing a hackathon project's specification, not writing code.
Read docs/02_master_spec.md, docs/03_architecture.md, and docs/07_tasks.md in this repo.
Do not produce any code. Instead:
1. Sanity-check the risk-rule sketch in docs/02_master_spec.md against the 8 sample
   contracts in data/raw/ and company_standards.json — flag any category where the
   deterministic rule would clearly misclassify one of the 8 contracts.
2. Review the explanation text your teammates draft for plain language and
   accuracy against the evidence — flag anything that reads like invented content.
3. Give feedback on the demo script in docs/12_demo_plan.md for clarity and timing.
Return findings as a plain list. Do not generate implementation code.
```

## Prompt for Claude Code / Antigravity IDE / Agy CLI / Opencode — implementation
```
You are an implementation agent working on this repository. Read agent.md first —
it is your operating manual and is non-negotiable.
Then read docs/02_master_spec.md and docs/03_architecture.md for the frozen design.
Pick up the next unblocked task from docs/07_tasks.md (check docs/09_progress.md
and docs/10_handoffs.md first to see what's already done and what's blocked).
Implement exactly that one task, respecting its Files Allowed / Files Forbidden.
Write/run the tests named in its Acceptance Criteria.
Before you stop, append an entry to docs/09_progress.md in the required format.
If you deviate from any frozen doc, add an ADR to docs/08_decisions.md first.
Do not touch docs/ unless the task explicitly allows it.
```

## Recommended Execution Order (4-hour budget)

| Time | Task(s) | Lane |
|---|---|---|
| 0:00–0:30 | T-01 Data Loader | Backend |
| 0:00–0:30 | T-07 (stub UI against mocked API, start in parallel) | Frontend |
| 0:30–1:10 | T-02 Clause Segmenter | Backend |
| 1:10–1:50 | T-03 Clause Classifier | Backend |
| 1:50–2:50 | T-04 Fact Extractor + Risk Rules (largest task — start early, don't slip) | Backend |
| 2:20–2:50 | T-08 Review History + About pages | Frontend |
| 2:50–3:20 | T-05 Explanation Builder | Backend / AI Integration |
| 3:20–4:00 | T-06 API Layer wiring everything together | Backend |
| 3:00–3:30 (parallel) | Continue T-07 against real API once T-06 stabilizes | Frontend |
| 3:30–4:00 | T-09 Test Suite (PQ-01..12, MI-01..03) | Testing |
| 3:50–4:10 | T-10 Demo rehearsal | Presentation |
| 4:00–4:15 | T-11 README + submission checklist pass | Documentation |

Note: total exceeds 4:00 slightly because lanes run in parallel — the backend critical path (T-01→T-02→T-03→T-04→T-06) is the ~3h10m bottleneck; frontend, testing, and docs lanes fit around it.
