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
- Say: "This is the case that matters most: when the information isn't there, the system says so instead of guessing. This is test case MI-01 from the organizers' own missing-information dataset — C-004, automatic renewal notice — and our result matches the expected safe behaviour exactly." *(Citing the ID directly, not just "one of the organizers' cases," makes this a verifiable claim rather than an assertion — confirmed against `missing_information_cases.json` ahead of time.)*

**2:15–2:50 — Human-in-the-loop**
- Back on C-001's result, click "Mark for review," add a one-line note, show the toast confirmation.
- Switch to Review History page → show the row with status + note.
- Say: "Nothing here is a final decision. Every result is logged and routed to a person."

**2:50–3:50 — How it prevents made-up answers (the judged question)**
- Say: "The risk label itself is never produced by a language model. It's computed by rules over numbers we extract directly from the contract and standard text — deadlines, notice periods, percentages. The model, if it's used at all, only rewrites the explanation sentence, and even then we check its output is grounded in the same evidence before we show it. If it isn't, we fall back to a template sentence built straight from the numbers."

**3:50–4:10 — Scaling & security (anticipated questions, compressed — expand only if judges ask)**
- Scaling: "Rules are config-driven per category, not per contract, so new contracts don't need new code as long as headings stay structured."
- Security/privacy: "Runs fully local today — no data leaves the machine unless the optional explanation step is on. Production would add auth, encryption at rest, and access logging on the review audit trail."

**4:10–4:30 — What we'd improve with more time**
- Broader clause-boundary detection for less-structured contracts.
- A confidence score alongside each risk label.
- Structured reviewer feedback loop back into the rule config.

*(Segments now total 4:30, leaving ~30s real buffer against the "under 5 minutes" target — this was previously exactly 5:00 with zero slack, per spec review.)*

## Rehearsal note (cold start)
Click through every tab at least once before judges arrive. The first-ever request to a freshly started backend triggers SQLite seeding (T-01) and will be slower than every request after it — don't let the first live click in front of judges also be the first-ever backend call.

## Fallback if the LLM/network is unavailable at venue
Demo runs identically — `USE_LLM_EXPLANATIONS=false` is the default and the entire required workflow (including PQ/MI cases) works with zero external calls. Mention this explicitly if asked about reliability.
