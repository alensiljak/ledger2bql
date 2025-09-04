"""
Tests for the currency uppercasing feature.
"""
import os
from unittest.mock import patch

from tests.test_utils import run_bal_command


@patch('os.getenv')
def test_currency_filter_uppercase(mock_getenv):
    """Test that currency filter automatically uppercases the currency code."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    # Act
    result = run_bal_command(['-c', 'eur'])

    # Assert
    assert result.exit_code == 0
    output = result.output
    # The query should use uppercase currency
    assert "currency = 'EUR'" in output
    # The output should show EUR currency
    assert "EUR" in output
    # The output should not show eur currency
    assert "eur" not in output