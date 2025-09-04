"""
Tests for the exchange currency uppercasing feature.
"""
import os

from tests.test_utils import run_bal_command, run_reg_command

def test_exchange_currency_uppercase_bal():
    """Test that exchange currency automatically uppercases the currency code in balance command."""

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

def test_exchange_currency_uppercase_reg():
    """Test that exchange currency automatically uppercases the currency code in register command."""

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