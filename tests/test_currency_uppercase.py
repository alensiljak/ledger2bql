"""
Tests for the currency uppercasing feature.
"""

from tests.test_utils import run_bal_command


def test_currency_filter_uppercase():
    """Test that currency filter automatically uppercases the currency code."""

    # Act
    result = run_bal_command(["-c", "eur"])

    # Assert
    assert result.exit_code == 0
    output = result.output
    # The query should use uppercase currency
    assert "currency = 'EUR'" in output
    # The output should show EUR currency
    assert "EUR" in output
    # The output should not show eur currency
    assert "eur" not in output
