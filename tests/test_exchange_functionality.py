"""
Tests for the exchange (-X) functionality.
"""

from tests.test_utils import run_bal_command, run_reg_command


def test_bal_exchange_eur_to_usd():
    """Test balance command with EUR to USD exchange."""

    # Act
    result = run_bal_command(["--exchange", "USD"])

    # Assert
    assert result.exit_code == 0
    output = result.output

    # The query should use convert function
    assert "convert(sum(position), 'USD')" in output

    # Should show converted balances
    assert "Total (USD)" in output


def test_reg_exchange_eur_to_usd():
    """Test register command with EUR to USD exchange."""

    # Act
    result = run_reg_command(["--exchange", "USD"])

    # Assert
    assert result.exit_code == 0
    output = result.output

    # The query should use convert function
    assert "convert(position, 'USD')" in output

    # Should show converted amounts
    assert "Amount" in output


def test_bal_exchange_with_total():
    """Test balance command with exchange and total."""

    # Act
    result = run_bal_command(["--exchange", "USD", "--total"])

    # Assert
    assert result.exit_code == 0
    output = result.output

    # Should show converted balances and total
    assert "Total (USD)" in output
    assert "Total" in output


def test_reg_exchange_with_total():
    """Test register command with exchange and total."""

    # Act
    result = run_reg_command(["--exchange", "USD", "--total"])

    # Assert
    assert result.exit_code == 0
    output = result.output

    # Should show converted amounts and running totals
    assert "Running Total" in output
