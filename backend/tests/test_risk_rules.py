import unittest
from backend.app.risk_rules import evaluate_risk
from backend.app.db import get_db_connection

class TestRiskRules(unittest.TestCase):
    def test_all_contracts(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test C-001
        cursor.execute("SELECT category, text, present FROM clauses WHERE contract_id = 'C-001'")
        clauses = {row["category"]: (row["text"] if row["present"] else None) for row in cursor.fetchall()}
        
        # Payment: 15 days -> Medium Risk
        risk, facts = evaluate_risk("Payment", clauses["Payment"])
        self.assertEqual(risk, "Medium Risk")
        self.assertEqual(facts["days_to_pay"], 15)
        
        # Termination: 30 days convenience -> Low Risk
        risk, facts = evaluate_risk("Termination", clauses["Termination"])
        self.assertEqual(risk, "Low Risk")
        self.assertEqual(facts["notice_days"], 30)
        
        # Automatic Renewal: 12mo term, 60 day notice -> High Risk (wait, standard is 30 day notice. 60 day notice is 2x standard notice -> High Risk)
        risk, facts = evaluate_risk("Automatic Renewal", clauses["Automatic Renewal"])
        self.assertEqual(risk, "High Risk")
        self.assertEqual(facts["renewal_months"], 12)
        self.assertEqual(facts["notice_days"], 60)
        
        # Liability: 1 month cap -> High Risk
        risk, facts = evaluate_risk("Limitation of Liability", clauses["Limitation of Liability"])
        self.assertEqual(risk, "High Risk")
        self.assertEqual(facts["cap_months"], 1)

        # Test C-002
        cursor.execute("SELECT category, text, present FROM clauses WHERE contract_id = 'C-002'")
        clauses_c002 = {row["category"]: (row["text"] if row["present"] else None) for row in cursor.fetchall()}
        
        # Payment: 100% prepayment -> High Risk
        risk, facts = evaluate_risk("Payment", clauses_c002["Payment"])
        self.assertEqual(risk, "High Risk")
        
        # Termination: Asymmetric grounds -> High Risk
        risk, facts = evaluate_risk("Termination", clauses_c002["Termination"])
        self.assertEqual(risk, "High Risk")
        
        # Confidentiality: Asymmetric, no duration -> High Risk
        risk, facts = evaluate_risk("Confidentiality", clauses_c002["Confidentiality"])
        self.assertEqual(risk, "High Risk")
        
        # IP: Vendor retains ownership, 6mo licence -> High Risk
        risk, facts = evaluate_risk("Intellectual Property", clauses_c002["Intellectual Property"])
        self.assertEqual(risk, "High Risk")
        
        # Automatic Renewal: Absent -> NEI
        risk, facts = evaluate_risk("Automatic Renewal", clauses_c002["Automatic Renewal"])
        self.assertEqual(risk, "Not Enough Information")

        # Test C-007 IP Low Risk compliant clause
        cursor.execute("SELECT category, text, present FROM clauses WHERE contract_id = 'C-007'")
        clauses_c007 = {row["category"]: (row["text"] if row["present"] else None) for row in cursor.fetchall()}
        
        risk, facts = evaluate_risk("Intellectual Property", clauses_c007["Intellectual Property"])
        self.assertEqual(risk, "Low Risk")
        
        # Liability: 12-month cap, missing carve-outs -> Medium Risk
        risk, facts = evaluate_risk("Limitation of Liability", clauses_c007["Limitation of Liability"])
        self.assertEqual(risk, "Medium Risk")
        
        # Confidentiality: 1 year, missing carve-outs -> High Risk
        risk, facts = evaluate_risk("Confidentiality", clauses_c007["Confidentiality"])
        self.assertEqual(risk, "High Risk")

        conn.close()

if __name__ == "__main__":
    unittest.main()
