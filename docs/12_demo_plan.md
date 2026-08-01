# 12 — Demo Plan

Target length: **under 5 minutes**, plus Q&A. Rehearse per T-10 at least twice before presenting.

## Script

**0:00–0:30 — Framing**
"This is a contract review assistant, not a legal-advice tool. It finds clauses, compares them to approved company standards, flags risk, and every single result requires human sign-off. Here's how it works."

**0:30–1:30 — Happy path (C-001, Automatic Renewal)**
- Select C-001 in the sidebar.
- Click "Automatic Renewal" tab → Run Review.
- Point at the Result Card: risk badge = High Risk, contract evidence quote (60-day notice), standard text + ID (STD-REN-01, ≤30 days), reason sentence.
- Say: "Every number in that sentence came from these two quotes on screen — nothing here was invented."

**1:30–2:15 — Abstention path (C-004, Automatic Renewal) — the key moment**
- Select C-004 → same tab → Run Review.
- Result: `Not Enough Information`, explanation states no renewal clause exists in this excerpt.
- Say: "This is the case that matters most: when the information isn't there, the system says so instead of guessing. This exact scenario is one of the organizers' own missing-information test cases."

**2:15–3:00 — Human-in-the-loop**
- Back on C-001's result, click "Mark for review," add a one-line note, show the toast confirmation.
- Switch to Review History page → show the row with status + note.
- Say: "Nothing here is a final decision. Every result is logged and routed to a person."

**3:00–4:00 — How it prevents made-up answers (the judged question)**
- Say: "The risk label itself is never produced by a language model. It's computed by rules over numbers we extract directly from the contract and standard text — deadlines, notice periods, percentages. The model, if it's used at all, only rewrites the explanation sentence, and even then we check its output is grounded in the same evidence before we show it. If it isn't, we fall back to a template sentence built straight from the numbers."

**4:00–4:30 — Scaling & security (anticipated questions)**
- Scaling: "The classifier and risk rules are config-driven per category, not hardcoded per contract, so adding contract #9 or #900 doesn't require new code — same rules apply as long as headings stay reasonably structured. For messier real-world contracts we'd add an LLM-assisted classification step, still with the same verification gate."
- Security/privacy: "Right now this runs entirely local — no data leaves the machine unless the optional LLM explanation step is turned on. In production we'd add auth, encrypt the SQLite store or move to a managed DB with row-level access control, and log every access to the review audit trail."

**4:30–5:00 — What we'd improve with more time**
- Broader clause-boundary detection for less-structured contracts.
- A confidence score alongside each risk label.
- Multi-clause cross-references (e.g. liability cap interacting with data breach clauses).
- Structured reviewer feedback loop back into the rule config.

## Fallback if the LLM/network is unavailable at venue
Demo runs identically — `USE_LLM_EXPLANATIONS=false` is the default and the entire required workflow (including PQ/MI cases) works with zero external calls. Mention this explicitly if asked about reliability.
