import unittest
from fastapi.testclient import TestClient
from backend.app.main import app

class TestMissingInformation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
    def test_mi_01_missing_renewal_c004(self):
        # MI-01: C-004, Automatic Renewal -> Not Enough Information
        response = self.client.post("/review", json={
            "contract_id": "C-004",
            "category": "Automatic Renewal"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["risk_level"], "Not Enough Information")
        self.assertIsNone(data["contract_evidence"])
        self.assertIsNone(data["standard_id"])
        self.assertIsNone(data["standard_text"])
        self.assertIn("no automatic renewal clause", data["reason"].lower())
        
    def test_mi_02_missing_termination_c007(self):
        # MI-02: C-007, Termination -> Not Enough Information
        response = self.client.post("/review", json={
            "contract_id": "C-007",
            "category": "Termination"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["risk_level"], "Not Enough Information")
        self.assertIsNone(data["contract_evidence"])
        self.assertIsNone(data["standard_id"])
        self.assertIsNone(data["standard_text"])
        self.assertIn("no termination clause", data["reason"].lower())

    def test_mi_03_missing_liability_c008(self):
        # MI-03: C-008, Limitation of Liability -> Not Enough Information
        response = self.client.post("/review", json={
            "contract_id": "C-008",
            "category": "Limitation of Liability"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["risk_level"], "Not Enough Information")
        self.assertIsNone(data["contract_evidence"])
        self.assertIsNone(data["standard_id"])
        self.assertIsNone(data["standard_text"])
        self.assertIn("no limitation of liability clause", data["reason"].lower())

if __name__ == "__main__":
    unittest.main()
