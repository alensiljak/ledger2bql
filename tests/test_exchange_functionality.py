"""
Tests for the exchange (-X) functionality.
"""
import os
from unittest.mock import patch

from tests.test_utils import run_bal_command, run_reg_command


@patch('os.getenv')
def test_bal_exchange_eur_to_usd(mock_getenv):
    """Test balance command with EUR to USD exchange."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    # Act
    result = run_bal_command(['--exchange', 'USD'])

    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The query should use convert function
    assert "convert(sum(position), 'USD')" in output
    
    # Should show converted balances
    assert "Total (USD)" in output


@patch('os.getenv')
def test_reg_exchange_eur_to_usd(mock_getenv):
    """Test register command with EUR to USD exchange."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    # Act
    result = run_reg_command(['--exchange', 'USD'])

    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The query should use convert function
    assert "convert(position, 'USD')" in output
    
    # Should show converted amounts
    assert "Amount" in output


@patch('os.getenv')
def test_bal_exchange_with_total(mock_getenv):
    """Test balance command with exchange and total."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    # Act
    result = run_bal_command(['--exchange', 'USD', '--total'])

    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # Should show converted balances and total
    assert "Total (USD)" in output
    assert "Total" in output


@patch('os.getenv')
def test_reg_exchange_with_total(mock_getenv):
    """Test register command with exchange and total."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    # Act
    result = run_reg_command(['--exchange', 'USD', '--total'])

    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # Should show converted amounts and running totals
    assert "Running Total" in output