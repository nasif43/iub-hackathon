import unittest
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.loader import load_all_data

class TestPublicQuestionsFull(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_all_data()
        cls.client = TestClient(app)
        
    def test_all_12_public_questions(self):
        with open("data/raw/public_test_questions.json", "r", encoding="utf-8") as f:
            questions = json.load(f)
            
        # Map contract and question to categories based on keywords/heuristics
        cat_map = {
            "PQ-01": "Automatic Renewal",
            "PQ-02": "Payment",
            "PQ-03": "Intellectual Property",
            "PQ-04": "Data Protection",
            "PQ-05": "Data Protection",
            "PQ-06": "Termination",
            "PQ-07": "Automatic Renewal",
            "PQ-08": "Intellectual Property",
            "PQ-09": "Limitation of Liability",
            "PQ-10": "Termination",
            "PQ-11": "Confidentiality",
            "PQ-12": "Automatic Renewal"
        }
        
        expected_risks = {
            "PQ-01": "High Risk",
            "PQ-02": "Medium Risk",
            "PQ-03": "High Risk",
            "PQ-04": "High Risk",
            "PQ-05": "High Risk",
            "PQ-06": "Low Risk", # C-004 termination is 30 days convenience -> Low Risk
            "PQ-07": "Not Enough Information", # C-004 has no automatic renewal
            "PQ-08": "High Risk", # C-005 IP custom retains -> High
            "PQ-09": "Low Risk", # C-006 Liability matches standards
            "PQ-10": "High Risk", # C-006 termination for breach immediate -> High
            "PQ-11": "High Risk", # C-007 Confidentiality 1 year -> High
            "PQ-12": "High Risk"  # C-008 renewal 24 months / 90 days -> High
        }
        
        for q in questions:
            qid = q["id"]
            cat = cat_map[qid]
            resp = self.client.post("/review", json={
                "contract_id": q["contract_id"],
                "category": cat
            })
            self.assertEqual(resp.status_code, 200, f"Failed for {qid}")
            data = resp.json()
            self.assertEqual(data["risk_level"], expected_risks[qid], f"Mismatch for {qid}: expected {expected_risks[qid]}, got {data['risk_level']}")

if __name__ == "__main__":
    unittest.main()
