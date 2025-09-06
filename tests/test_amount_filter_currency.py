"""
Tests for the amount filter currency uppercasing feature.
"""

import unittest
from src.ledger2bql.utils import parse_amount_filter


class TestAmountFilterCurrencyUppercasing(unittest.TestCase):
    def test_amount_filter_currency_uppercase(self):
        """Test that amount filter automatically uppercases the currency code."""
        # Test with lowercase currency
        op, val, cur = parse_amount_filter(">100eur")
        self.assertEqual(op, ">")
        self.assertEqual(val, 100)
        self.assertEqual(cur, "EUR")

        # Test with mixed case currency
        op, val, cur = parse_amount_filter(">=50.50UsD")
        self.assertEqual(op, ">=")
        self.assertEqual(val, 50.50)
        self.assertEqual(cur, "USD")

        # Test with already uppercase currency
        op, val, cur = parse_amount_filter("<200GBP")
        self.assertEqual(op, "<")
        self.assertEqual(val, 200)
        self.assertEqual(cur, "GBP")

        # Test without currency
        op, val, cur = parse_amount_filter("=100")
        self.assertEqual(op, "=")
        self.assertEqual(val, 100)
        self.assertIsNone(cur)


if __name__ == "__main__":
    unittest.main()
