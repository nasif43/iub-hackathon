# agent.md — Universal AI Operating Manual

This file governs how **any** AI coding agent (Claude Code, Antigravity IDE, Agy CLI, Opencode, Cursor, or any future agent) works on this repository. It is written to require zero hidden chat context — everything an agent needs is in `docs/`.

## You are an implementer, not a planner
All planning, architecture, schema, and API decisions are frozen in `docs/`. Your job is to execute one task at a time from `docs/07_tasks.md`. If a task requires a decision not covered in `docs/`, stop and record it as a blocker in `docs/09_progress.md` rather than guessing.

## Non-negotiable operating rules

1. **Documentation-first.** Before writing code for a task, re-read the relevant doc(s) referenced in that task's Dependencies field. If a doc and the codebase disagree, the doc wins unless there's a dated ADR in `08_decisions.md` overriding it — and if there isn't one, don't silently pick a side, add the ADR yourself first.

2. **One task at a time.** Work exactly one task ID from `07_tasks.md` per work session. Do not start a second task before finishing, blocking-and-logging, or explicitly handing off the first.

3. **Never assume hidden context.** Do not rely on a previous chat, a previous agent's reasoning, or anything not written down in `docs/`. If something seems implied but isn't written, write it down (as an ADR or a progress note) before acting on the assumption.

4. **Never silently change the API.** `05_api.md` is frozen. If you must change an endpoint shape, add an ADR in `08_decisions.md` explaining why, then update `05_api.md` in the same session — never leave the doc and the code disagreeing.

5. **Never silently change the architecture.** Same rule for `03_architecture.md` and `04_database.md`. In particular: **do not move the risk-level decision into an LLM call.** That is the single most important architectural invariant in this project (see `02_master_spec.md` Core Principle and ADR-001). If you think it should change, that's an ADR, not a quiet refactor.

6. **Update progress before stopping.** Every session — whether the task finished, partially finished, or got blocked — ends with an entry appended to `docs/09_progress.md` in the required format. This is not optional and is not the last thing you do "if there's time"; it's part of the task.

7. **Produce structured handoffs.** If you're stopping because work is moving to a different agent or person (not just pausing your own session), also append an entry to `docs/10_handoffs.md`.

8. **Record architectural decisions, don't just make them.** Any time you deviate from what's written, or resolve an ambiguity the docs didn't cover, add an ADR entry to `08_decisions.md` in the same session.

9. **Record blockers instead of guessing.** If a task can't proceed (missing info, a genuinely ambiguous requirement, a failing dependency), write the blocker plainly in `09_progress.md` and stop — do not fabricate a plausible-sounding resolution and move on. This mirrors the product's own core safety rule: uncertain → say so, don't invent.

10. **Respect Files Allowed / Files Forbidden per task.** Don't touch `docs/` while implementing a code task unless the task explicitly allows it (e.g. T-10, T-11). Don't touch backend/ from a frontend task or vice versa — that's the whole point of the parallelization boundary in `03_architecture.md`.

## Session checklist (run through this every time)
- [ ] Read the task's Objective, Description, Dependencies, and Files Allowed/Forbidden.
- [ ] Re-read any doc it depends on — don't rely on memory of it.
- [ ] Implement only within Files Allowed.
- [ ] Run/write the tests named in Acceptance Criteria.
- [ ] Append a `09_progress.md` entry.
- [ ] If handing off to a different agent/person, append a `10_handoffs.md` entry too.
- [ ] If you deviated from a frozen doc, add an ADR in `08_decisions.md` and update the doc.

## Anti-hallucination reminder specific to this project
This product's entire safety story rests on evidence being verbatim and risk levels being rule-derived, not generated. If you're implementing `explain.py` or anything LLM-adjacent, the verification step (checking the LLM's output doesn't introduce facts absent from the evidence) is not optional polish — it is a required part of the task, not something to add "later."
