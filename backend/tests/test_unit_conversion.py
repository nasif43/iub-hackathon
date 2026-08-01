import unittest
import os
from unittest.mock import patch
from backend.app.facts import (
    extract_number_from_text,
    llm_fallback_extract
)

class TestUnitConversionAndFallback(unittest.TestCase):

    def test_weeks_to_days_conversion(self):
        # Under 30-day payment threshold (e.g. 3 weeks = 21 days -> Medium Risk)
        days_under, src1 = extract_number_from_text("Payment is due within 3 weeks of invoice.", ["day", "days"])
        self.assertEqual(days_under, 21)
        self.assertEqual(src1, "rule_engine")

        # Over 30-day payment threshold (e.g. 5 weeks = 35 days -> Low Risk)
        days_over, src2 = extract_number_from_text("Payment is due within 5 weeks of invoice.", ["day", "days"])
        self.assertEqual(days_over, 35)
        self.assertEqual(src2, "rule_engine")

    def test_business_weeks_to_business_days_conversion(self):
        # 2 business weeks = 10 business days (at cure threshold)
        cure_days, src = extract_number_from_text("The breaching party has 2 business weeks to cure the breach.", ["day", "days"])
        self.assertEqual(cure_days, 10)
        self.assertEqual(src, "rule_engine")

    def test_quarters_to_months_conversion(self):
        # 1 quarter = 3 months
        months_1, src1 = extract_number_from_text("The initial term is 1 quarter.", ["month", "months"])
        self.assertEqual(months_1, 3)
        self.assertEqual(src1, "rule_engine")

        # 4 quarters = 12 months (at 12-month renewal / liability cap window)
        months_4, src2 = extract_number_from_text("Liability is capped at fees paid over four quarters.", ["month", "months"])
        self.assertEqual(months_4, 12)
        self.assertEqual(src2, "rule_engine")

    def test_no_unit_recognized_without_llm(self):
        # Nonsense phrasing when USE_LLM_FACT_EXTRACTION=false -> return None
        with patch.dict(os.environ, {"USE_LLM_FACT_EXTRACTION": "false"}):
            val, src = extract_number_from_text("Payment terms are governed by ancient lunar cycles.", ["day", "days"])
            self.assertIsNone(val)
            self.assertEqual(src, "rule_engine")

    @patch("urllib.request.urlopen")
    def test_llm_verification_gate_discards_hallucinated_number(self, mock_urlopen):
        # Mock OpenRouter returning value 999 which does NOT appear in source text
        class MockResponse:
            def read(self):
                return b'{"choices": [{"message": {"content": "{\\"value\\": 999, \\"unit\\": \\"days\\"}"}}]}'
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass

        mock_urlopen.return_value = MockResponse()

        with patch.dict(os.environ, {"USE_LLM_FACT_EXTRACTION": "true", "OPENROUTER_API_KEY": "sk-test"}):
            val = llm_fallback_extract("Payment must be made within reasonable time.", ["day", "days"])
            # Assert verification gate rejected 999 because "999" is not in the source text
            self.assertIsNone(val)

if __name__ == "__main__":
    unittest.main()
