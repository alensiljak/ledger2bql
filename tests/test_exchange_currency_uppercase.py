"""
Tests for the exchange currency uppercasing feature.
"""
import os
from unittest.mock import patch

from tests.test_utils import run_bal_command, run_reg_command


@patch('os.getenv')
def test_exchange_currency_uppercase_bal(mock_getenv):
    """Test that exchange currency automatically uppercases the currency code in balance command."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    # Act
    result = run_bal_command(['-X', 'chf'])

    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The query should use uppercase currency
    assert "convert(sum(position), 'CHF')" in output
    # The output should show CHF currency
    assert "Total (CHF)" in output
    # The output should not show chf currency
    assert "Total (chf)" not in output


@patch('os.getenv')
def test_exchange_currency_uppercase_reg(mock_getenv):
    """Test that exchange currency automatically uppercases the currency code in register command."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    # Act
    result = run_reg_command(['-X', 'chf'])

    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The query should use uppercase currency
    assert "convert(position, 'CHF')" in output
    # The output should show CHF currency
    assert "Amount (CHF)" in output
    # The output should not show chf currency
    assert "Amount (chf)" not in output