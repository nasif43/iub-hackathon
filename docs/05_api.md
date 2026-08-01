# 05 — API Specification

**Ground truth is `api.yml`** (OpenAPI 3.0, repo root). This document is a human-readable companion — if the two ever disagree, `api.yml` wins; fix the disagreement by updating both in the same change and recording why in `08_decisions.md`.

Base URL: `http://localhost:8000`. No auth (see NFR-03 — explicitly out of scope for this build).
All responses `application/json`. All errors follow the Error schema at the bottom.


---

### `GET /contracts`
List all contracts.
**Auth:** none
**Response 200:**
```json
[{"id": "C-001", "title": "BrightDesk SaaS Subscription Agreement", "parties": "Northstar Solutions Ltd. and BrightDesk Software Ltd."}]
```

---

### `GET /contracts/{contract_id}`
Get one contract, including raw text and dataset note.
**Errors:** 404 if contract_id unknown.

---

### `GET /contracts/{contract_id}/clauses`
List detected clause blocks for a contract (all 7 categories, `present` flag shows which exist).
**Response 200:**
```json
[{"category": "Payment", "present": true, "heading": "2.1 Payment", "text": "The Customer must pay..."},
 {"category": "Automatic Renewal", "present": false, "heading": null, "text": null}]
```

---

### `GET /standards`
List all 7 company standards.
**Response 200:**
```json
[{"id": "STD-PAY-01", "category": "Payment", "text": "The company should pay undisputed invoices..."}]
```

---

### `POST /review`
Run the full workflow for one contract + one category and persist the result as a pending review.
**Request:**
```json
{"contract_id": "C-001", "category": "Automatic Renewal"}
```
**Validation:**
- `contract_id` must exist (404 otherwise)
- `category` must be one of the 7 fixed strings (422 otherwise)

**Response 200 (found clause):**
```json
{
  "review_id": 17,
  "contract_id": "C-001",
  "category": "Automatic Renewal",
  "risk_level": "High Risk",
  "reason": "The contract requires 60 days' notice to cancel, which exceeds the 30-day standard.",
  "contract_evidence": "The Agreement automatically renews for another 12-month term unless the Customer gives written notice at least 60 days before the current term ends.",
  "standard_id": "STD-REN-01",
  "standard_text": "An automatic renewal period must not be longer than 12 months. The customer should not be required to give more than 30 days notice to stop renewal. A renewal reminder should be sent at least 45 days before the renewal date.",
  "source": "rule_engine",
  "status": "pending",
  "human_review": "Required"
}
```

**Response 200 (missing information — e.g. MI-01):**
```json
{
  "review_id": 18,
  "contract_id": "C-004",
  "category": "Automatic Renewal",
  "risk_level": "Not Enough Information",
  "reason": "This contract excerpt contains no automatic renewal clause. No notice period can be reported without inventing one.",
  "contract_evidence": null,
  "standard_id": null,
  "standard_text": null,
  "source": "rule_engine",
  "status": "pending",
  "human_review": "Required"
}
```

---

### `GET /reviews`
List all past reviews (audit trail), optionally filtered.
**Query params:** `contract_id` (optional), `status` (optional)

---

### `POST /reviews/{review_id}/decision`
Human reviewer records a decision.
**Request:**
```json
{"status": "approved", "reviewer_note": "Confirmed, escalate to legal for renegotiation."}
```
**Validation:** `status` must be one of `approved`, `rejected`, `marked_for_review`. `reviewer_note` optional string.
**Response 200:** the updated review row.
**Errors:** 404 if review_id unknown, 422 if status invalid.

---

## Error Schema (all 4xx/5xx responses)
```json
{"error": true, "code": "NOT_FOUND", "message": "Contract C-999 does not exist."}
```
Codes used: `NOT_FOUND`, `VALIDATION_ERROR`, `INTERNAL_ERROR`.
