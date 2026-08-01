# 03 — Architecture (Frozen Before Implementation)

## Stack (frozen)
- **Language:** Python 3.11 (single language end-to-end — easiest for AI coding agents to hand off between each other, no context-switch cost)
- **Backend:** FastAPI (REST) + Pydantic schemas
- **Frontend:** Streamlit (single app, multi-page via `st.tabs` / `st.sidebar` selector) — fastest to demo, no build step
- **Storage:** SQLite file (`data/cra.db`), loaded/seeded from the provided JSON/txt at startup
- **LLM (optional, toggleable):** Groq or OpenRouter (free/low-cost inference — see ADR-011), used *only* for explanation phrasing, gated by `USE_LLM_EXPLANATIONS` env var; system runs fully and correctly with it **off**
- **No** vector DB, **no** external search, **no** Docker requirement (nice-to-have, not required for the 4-hour build)

## Why this stack (for the "how would you defend this" question)
- Single language → any teammate or any AI coding agent (Claude Code, Antigravity, Agy CLI, Opencode) can move between backend/frontend/tests without a mental model switch.
- FastAPI gives you free request validation + auto-docs (`/docs`) — useful for judges poking at the API live.
- Streamlit avoids a JS build pipeline entirely — zero risk of a broken `npm run build` five minutes before demo.
- SQLite is a single file — trivially inspectable, trivially resettable, zero infra.

## Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Streamlit UI                         │
│  contract picker → category tabs → result card → review     │
│  actions (Approve/Reject/Mark/Feedback)                      │
└───────────────────────────┬───────────────────────────────┘
                            │ HTTP (localhost)
┌───────────────────────────▼───────────────────────────────┐
│                       FastAPI Backend                       │
│                                                              │
│  Data Loader        → reads C-00N.txt + company_standards   │
│                        .json at startup, seeds SQLite       │
│                                                              │
│  Clause Segmenter    → splits raw text into (heading, body)  │
│                        blocks using a numbered-heading regex │
│                                                              │
│  Clause Classifier   → maps each block to one of the 7       │
│                        categories via keyword rules over the │
│                        heading text (fallback: body keywords)│
│                                                              │
│  Standard Matcher    → category → standard, 1:1 dict lookup  │
│                                                              │
│  Fact Extractor      → regex pulls numbers + units (days,    │
│                        months, %, hours) from clause + std   │
│                                                              │
│  Risk Comparator     → per-category deterministic rule set   │
│                        (see 02_master_spec.md) → risk_level  │
│                                                              │
│  Explanation Builder → template sentence from extracted facts│
│                        OPTIONAL: LLM rewrite, verified against│
│                        source text before use, else discarded│
│                                                              │
│  Evidence Assembler  → packages verbatim contract text,       │
│                        verbatim standard text, standard ID   │
│                                                              │
│  Review Store        → SQLite: writes each result as a        │
│                        pending review; exposes decision API  │
└───────────────────────────┬───────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   SQLite file   │
                    │   data/cra.db   │
                    └────────────────┘
```

## Frozen Folder Structure
```
project/
  agent.md
  docs/                     # this documentation set
  data/
    raw/                    # provided C-001..C-008.txt, company_standards.json,
                             # public_test_questions.json, missing_information_cases.json
    cra.db                  # generated SQLite file (gitignored, regenerated on startup)
  backend/
    app/
      main.py               # FastAPI app entrypoint
      models.py              # Pydantic schemas (request/response)
      db.py                  # SQLite connection + schema creation
      loader.py               # reads raw/ into SQLite on startup
      segmenter.py             # clause segmentation
      classifier.py            # category classification (keyword rules, config-driven)
      standards.py              # category -> standard lookup
      facts.py                   # regex fact extraction
      risk_rules.py               # deterministic comparator per category
      explain.py                    # template explanation + optional LLM verification wrapper
      review.py                      # review CRUD (approve/reject/mark/feedback)
    tests/
      test_classifier.py
      test_risk_rules.py
      test_missing_information.py   # MI-01, MI-02, MI-03 must pass
      test_public_questions.py      # PQ-01..PQ-12 sanity checks
  frontend/
    streamlit_app.py
  .env.example
  requirements.txt
  README.md
```

## Environment Variables (frozen — do not add silently, record any new var in 08_decisions.md)
```
LLM_PROVIDER=groq             # "groq" or "openrouter" — only relevant if USE_LLM_EXPLANATIONS=true
GROQ_API_KEY=                 # set if LLM_PROVIDER=groq
OPENROUTER_API_KEY=           # set if LLM_PROVIDER=openrouter
LLM_MODEL=                    # e.g. a Groq-hosted Llama/Mixtral model, or an OpenRouter model string
USE_LLM_EXPLANATIONS=false    # default OFF; system must work fully without it
BACKEND_URL=http://localhost:8000
DB_PATH=./data/cra.db
```

## Interfaces (contract between backend and frontend — see 05_api.md and api.yml for full spec)
The frontend talks to the backend **only** through the REST API defined in `api.yml`. No direct DB or file access from the frontend. This is the parallelization boundary.

## Running Two Independent Devices in Parallel

`api.yml` is the one file both devices need before they start — after that, they don't need to talk to each other again until the final integration run.

**Device A — Backend:**
1. Read `api.yml` + `agent.md` + `03_architecture.md`/`04_database.md`.
2. Implement T-01 → T-06 exactly to the schemas/paths in `api.yml`.
3. Serve on `http://localhost:8000`; FastAPI's auto-docs at `/docs` should match `api.yml` (if they diverge, `api.yml` is still ground truth — fix the code).

**Device B — Frontend:**
1. Read `api.yml` + `06_frontend.md`.
2. Spin up a mock server directly from `api.yml` so there's zero dependency on backend progress:
   ```bash
   npm install -g @stoplight/prism-cli
   prism mock api.yml --port 8000
   ```
   Prism serves the exact example responses embedded in `api.yml` (`foundClause`, `notEnoughInformation`, etc.) for every endpoint — the Streamlit app in T-07/T-08 can be built and clicked through end-to-end against this mock, including the abstention path, before a single line of backend code exists.
3. Build `frontend/streamlit_app.py` pointed at `BACKEND_URL=http://localhost:8000` (the mock, for now).

**Final integration (both devices, same room or same call):**
1. Stop the Prism mock.
2. Start the real FastAPI backend on port 8000.
3. Point the frontend at the same `BACKEND_URL` — no code change needed if it was built against `api.yml` correctly, only the process behind port 8000 changed.
4. Run T-09's test suite against the real backend; run the demo script in `12_demo_plan.md` once end-to-end.

If either device needs to change a request/response shape mid-build, that's not a quiet Slack message — update `api.yml` first, add an ADR in `08_decisions.md`, then both devices pull the updated file. This is what keeps the two tracks genuinely independent instead of accidentally coupled through verbal agreements no one wrote down.

## What is explicitly NOT part of this architecture
Vector search, RAG, embeddings, Docker, auth/login, multi-user concurrency handling beyond SQLite defaults, cloud deployment, CI pipeline.
