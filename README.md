# Contract Review Assistant — Hackathon Project Package

This repository contains **documentation only** (no implementation), produced by the Project Orchestrator process. It is designed to be handed to implementation agents (Claude Code, Antigravity IDE, Agy CLI, Opencode) with zero reliance on prior chat history.

## Start here
1. `agent.md` — operating manual, read this first if you're an implementation agent.
2. `api.yml` — the ground-truth API contract (OpenAPI 3.0). Both the frontend device and the backend device build against this file, not against each other. See `docs/03_architecture.md` → "Running Two Independent Devices in Parallel" for the mock-server workflow.
3. `docs/00_problem.md` through `docs/13_submission_checklist.md`, in order.
4. `docs/14_next_steps.md` — exact prompts to hand to each tool, plus the recommended 4-hour execution schedule.

## Provided source data (place under `data/raw/` before implementation begins)
- `company_standards.json`
- `C-001.txt` … `C-008.txt`
- `public_test_questions.json`
- `missing_information_cases.json`
