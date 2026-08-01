import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

CONTRACTS = [
    {
        "id": "C-001",
        "title": "BrightDesk SaaS Subscription Agreement",
        "parties": "Northstar Solutions Ltd. and BrightDesk Software Ltd."
    },
    {
        "id": "C-004",
        "title": "Apex Cloud Master Services Agreement",
        "parties": "Northstar Solutions Ltd. and Apex Cloud Services LLC"
    }
]

CONTRACT_CLAUSES = {
    "C-001": [
        {"category": "Payment", "present": True, "heading": "2.1 Payment", "text": "Pay within 15 days."},
        {"category": "Automatic Renewal", "present": True, "heading": "5.2 Renewal", "text": "Renews for 12 months unless notice given 60 days before."}
    ],
    "C-004": [
        {"category": "Payment", "present": True, "heading": "3.1 Fees", "text": "Net 30 days."},
        {"category": "Automatic Renewal", "present": False, "heading": None, "text": None}
    ]
}

REVIEW_RESULTS = {
    ("C-001", "Automatic Renewal"): {
        "review_id": 17,
        "contract_id": "C-001",
        "category": "Automatic Renewal",
        "risk_level": "High Risk",
        "reason": "The contract requires 60 days' notice to cancel, which exceeds the 30-day standard.",
        "contract_evidence": "The Agreement automatically renews for another 12-month term unless the Customer gives written notice at least 60 days before the current term ends.",
        "standard_id": "STD-REN-01",
        "standard_text": "An automatic renewal period must not be longer than 12 months. The customer should not be required to give more than 30 days notice to stop renewal.",
        "source": "rule_engine",
        "status": "pending",
        "human_review": "Required"
    },
    ("C-004", "Automatic Renewal"): {
        "review_id": 18,
        "contract_id": "C-004",
        "category": "Automatic Renewal",
        "risk_level": "Not Enough Information",
        "reason": "This contract excerpt contains no automatic renewal clause. No notice period can be reported without inventing one.",
        "contract_evidence": None,
        "standard_id": None,
        "standard_text": None,
        "source": "rule_engine",
        "status": "pending",
        "human_review": "Required"
    }
}

REVIEWS_DB = list(REVIEW_RESULTS.values())

class MockAPIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == "/contracts":
            self._send_json(CONTRACTS)
        elif path.startswith("/contracts/") and path.endswith("/clauses"):
            cid = path.split("/")[2]
            clauses = CONTRACT_CLAUSES.get(cid, [
                {"category": cat, "present": True, "heading": f"1.0 {cat}", "text": "Sample clause text"}
                for cat in ["Payment", "Termination", "Data Protection", "Confidentiality", "Automatic Renewal", "Intellectual Property", "Limitation of Liability"]
            ])
            self._send_json(clauses)
        elif path == "/reviews":
            query = parse_qs(parsed.query)
            filtered = REVIEWS_DB
            if "contract_id" in query:
                filtered = [r for r in filtered if r.get("contract_id") == query["contract_id"][0]]
            if "status" in query and query["status"][0] != "All":
                filtered = [r for r in filtered if r.get("status") == query["status"][0]]
            self._send_json(filtered)
        else:
            self._send_json({"error": True, "code": "NOT_FOUND", "message": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}

        if path == "/review":
            cid = body.get("contract_id")
            cat = body.get("category")
            res = REVIEW_RESULTS.get((cid, cat), {
                "review_id": len(REVIEWS_DB) + 1,
                "contract_id": cid,
                "category": cat,
                "risk_level": "Low Risk",
                "reason": f"Sample response for {cat}",
                "contract_evidence": "Sample evidence text",
                "standard_id": "STD-SAMPLE",
                "standard_text": "Sample standard text",
                "source": "rule_engine",
                "status": "pending",
                "human_review": "Required"
            })
            if res not in REVIEWS_DB:
                REVIEWS_DB.append(res)
            self._send_json(res)
        elif path.startswith("/reviews/") and path.endswith("/decision"):
            rid = int(path.split("/")[2])
            for r in REVIEWS_DB:
                if r.get("review_id") == rid:
                    r["status"] = body.get("status", r["status"])
                    r["reviewer_note"] = body.get("reviewer_note")
                    self._send_json(r)
                    return
            self._send_json({"error": True, "code": "NOT_FOUND", "message": "Review not found"}, 404)

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), MockAPIHandler)
    print("Mock API running on port 8000...")
    server.serve_forever()
