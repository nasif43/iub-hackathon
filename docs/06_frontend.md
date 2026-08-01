# 06 — Frontend Specification (Streamlit, frozen)

Single Streamlit app (`frontend/streamlit_app.py`), talks only to the REST API in `05_api.md`.

## Pages / Layout (Streamlit "pages" = sidebar sections, not separate routes)

### Page 1 — Review
- **Sidebar:** contract picker (`selectbox`, populated from `GET /contracts`) → shows title + parties on selection.
- **Main area:** 7 category tabs (`st.tabs`), one per fixed category. Selecting a tab that isn't `present` for this contract still allows clicking "Run Review" — this is exactly how the NEI path gets demonstrated live.
- **"Run Review" button** → calls `POST /review` → renders a **Result Card**:
  - Header: `Contract ID` + `Clause Type`
  - Colored risk badge: Low Risk (green), Medium Risk (yellow), High Risk (red), Not Enough Information (grey)
  - "Contract Evidence" expandable block (verbatim quote, or "No clause found" message)
  - "Company Standard" block (standard ID + verbatim text, or "N/A — not applicable" for NEI)
  - "Reason" paragraph
  - Fixed banner, always visible, never dismissible: **"Human Review Required — this is not legal advice."**
  - Review action row: `Approve` / `Reject` / `Mark for review` buttons + a text input for `Add feedback` → all call `POST /reviews/{id}/decision`

### Page 2 — Review History
- Table (`st.dataframe`) of all past reviews from `GET /reviews`, filterable by contract and status.
- Read-only; lets judges see the audit trail exists.

### Page 3 — About / Safety Notes (static content)
- One paragraph restating: not legal advice, human-in-the-loop, evidence-based, rule-engine-first architecture. This exists purely so judges can find the disclaimer without you needing to say it verbally every time.

## State (Streamlit `session_state` keys)
- `selected_contract_id`
- `selected_category`
- `last_review_result` (dict from the API response, re-rendered until a new review runs)
- `status_message` (transient success/error toast text)

## User Flow (happy path)
1. Open app → contract list loads → pick C-001.
2. Click "Automatic Renewal" tab → click "Run Review" → Result Card appears with High Risk + evidence.
3. Click "Mark for review" → note persists → confirmation toast.
4. Switch to Review History → see the row.

## User Flow (abstention path — MI-01 demo)
1. Pick C-004.
2. Click "Automatic Renewal" tab (not present for this contract).
3. Click "Run Review" → Result Card shows `Not Enough Information`, contract evidence area shows "No automatic renewal clause found in this excerpt," standard area shows "N/A."
4. This is the single most important moment of the demo — see `12_demo_plan.md`.

## Responsive behavior
Streamlit's default layout is single-column and reflows acceptably on narrow viewports; no custom CSS required for this build. If time remains, `st.set_page_config(layout="wide")` for judge laptops, but this is optional polish, not a requirement.
