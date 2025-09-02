"""
Tests for the currency uppercasing feature.
"""
import argparse
import os
from io import StringIO
from unittest.mock import patch

from src.ledger2bql.ledger_bal_to_bql import main as bal_main
from src.ledger2bql.utils import add_common_arguments


@patch('os.getenv')
def test_currency_filter_uppercase(mock_getenv):
    """Test that currency filter automatically uppercases the currency code."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'tests', 'sample_ledger.bean')
    )

    f = StringIO()
    with patch('sys.stdout', f):
        with patch('sys.argv', ['bal', '-c', 'eur']):
            # Act
            bal_main()

    # Assert
    output = f.getvalue()
    # The query should use uppercase currency
    assert "currency = 'EUR'" in output
    # The output should show EUR currency
    assert "EUR" in output
    # The output should not show eur currency
    assert "eur" not in output


def test_currency_argument_uppercase():
    """Test that currency argument is automatically uppercased."""
    parser = argparse.ArgumentParser()
    add_common_arguments(parser)
    
    # Test with lowercase currency
    args = parser.parse_args(['-c', 'eur'])
    assert args.currency == 'EUR', f"Expected 'EUR', got '{args.currency}'"
    
    # Test with mixed case currency
    args = parser.parse_args(['-c', 'UsD'])
    assert args.currency == 'USD', f"Expected 'USD', got '{args.currency}'"
    
    # Test with already uppercase currency
    args = parser.parse_args(['-c', 'GBP'])
    assert args.currency == 'GBP', f"Expected 'GBP', got '{args.currency}'"