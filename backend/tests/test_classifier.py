import unittest
from backend.app.segmenter import segment_contract
from backend.app.classifier import classify_clause

class TestClassifier(unittest.TestCase):
    def test_segmenter_c001(self):
        text = """Contract ID: C-001
Title: BrightDesk SaaS Subscription Agreement
Parties: Northstar Solutions Ltd. and BrightDesk Software Ltd.

2.1 Payment
The Customer must pay each undisputed invoice within 15 calendar days after the invoice date.

5.2 Termination
Either party may terminate this Agreement for convenience by giving the other party 30 days written notice.

Dataset Note:
This excerpt does not include a data protection clause."""
        blocks = segment_contract(text)
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0][0], "2.1 Payment")
        self.assertEqual(blocks[0][1], "The Customer must pay each undisputed invoice within 15 calendar days after the invoice date.")
        self.assertEqual(blocks[1][0], "5.2 Termination")
        self.assertEqual(blocks[1][1], "Either party may terminate this Agreement for convenience by giving the other party 30 days written notice.")

    def test_classification_c001(self):
        self.assertEqual(classify_clause("2.1 Payment", "The Customer must pay each undisputed invoice within 15 calendar days after the invoice date."), "Payment")
        self.assertEqual(classify_clause("5.2 Termination", "Either party may terminate this Agreement for convenience by giving the other party 30 days written notice."), "Termination")

if __name__ == "__main__":
    unittest.main()
