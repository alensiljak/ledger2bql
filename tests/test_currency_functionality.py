"""
Tests for the currency parameter functionality.
"""
import os
from unittest.mock import patch

from tests.test_utils import run_bal_command, run_reg_command, extract_table_data


@patch('os.getenv')
def test_bal_currency_filter_eur(mock_getenv):
    """Test balance command with EUR currency filter."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    # Act
    result = run_bal_command(['--currency', 'eur'])

    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The query should use uppercase currency
    assert "currency = 'EUR'" in output
    
    # Extract table data
    table_lines = extract_table_data(output.splitlines())
    table_output = "\n".join(table_lines)
    
    # Should show accounts with EUR currency
    assert "| Assets:Bank:Checking     |  1,884.65 EUR |" in table_output
    assert "| Assets:Cash:Pocket-Money |    -20.00 EUR |" in table_output
    assert "| Equity:Opening-Balances  | -1,000.00 EUR |" in table_output
    assert "| Expenses:Food            |    100.00 EUR |" in table_output
    assert "| Expenses:Sweets          |     20.00 EUR |" in table_output
    assert "| Income:Salary            | -1,000.00 EUR |" in table_output
    
    # Should not show accounts with only BAM currency
    assert "| Assets:Cash:BAM | -25.00 BAM |" not in table_output


@patch('os.getenv')
def test_bal_currency_filter_bam(mock_getenv):
    """Test balance command with BAM currency filter."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    # Act
    result = run_bal_command(['--currency', 'bam'])

    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The query should use uppercase currency
    assert "currency = 'BAM'" in output
    
    # Extract table data
    table_lines = extract_table_data(output.splitlines())
    table_output = "\n".join(table_lines)
    
    # Should show accounts with BAM currency
    assert "| Assets:Cash:BAM | -25.00 BAM |" in table_output
    assert "| Expenses:Food   |  25.00 BAM |" in table_output
    
    # Should not show accounts with only EUR currency
    assert "| Assets:Bank:Checking     |  1,884.65 EUR |" not in table_output
    assert "| Assets:Cash:Pocket-Money |    -20.00 EUR |" not in table_output


@patch('os.getenv')
def test_bal_currency_filter_abc(mock_getenv):
    """Test balance command with ABC currency filter."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    # Act
    result = run_bal_command(['--currency', 'abc'])

    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The query should use uppercase currency
    assert "currency = 'ABC'" in output
    
    # Extract table data
    table_lines = extract_table_data(output.splitlines())
    table_output = "\n".join(table_lines)
    
    # Should show accounts with ABC currency
    assert "| Equity:Stocks | 12.00 ABC |" in table_output
    
    # Should not show accounts with other currencies
    assert "| Assets:Bank:Checking     |  1,884.65 EUR |" not in table_output
    assert "| Assets:Cash:BAM | -25.00 BAM |" not in table_output


@patch('os.getenv')
def test_reg_currency_filter_abc(mock_getenv):
    """Test register command with ABC currency filter."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    # Act
    result = run_reg_command(['--currency', 'abc'])

    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The query should use uppercase currency
    assert "currency = 'ABC'" in output
    
    # Should show transactions with ABC currency
    assert "ABC" in output
    assert "Equity:Stocks" in output
    
    # Should not show transactions with other currencies (unless they also have ABC)


@patch('os.getenv')
def test_currency_uppercase_conversion(mock_getenv):
    """Test that currency codes are automatically uppercased."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    # Test with lowercase currency that exists in the ledger
    result = run_bal_command(['-c', 'eur'])

    # Assert - the query should use uppercase currency
    assert result.exit_code == 0
    output = result.output
    assert "currency = 'EUR'" in output
    assert "currency = 'eur'" not in output

    # Test with mixed case currency that exists in the ledger
    result = run_bal_command(['-c', 'AbC'])

    # Assert - the query should use uppercase currency
    assert result.exit_code == 0
    output = result.output
    assert "currency = 'ABC'" in output
    assert "currency = 'AbC'" not in output


@patch('os.getenv')
def test_bal_multiple_currency_filter(mock_getenv):
    """Test balance command with multiple currency filter."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    # Act
    result = run_bal_command(['--currency', 'eur,bam'])

    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The query should use IN clause for multiple currencies
    assert "currency IN ('EUR', 'BAM')" in output
    
    # Extract table data
    table_lines = extract_table_data(output.splitlines())
    table_output = "\n".join(table_lines)
    
    # Should show accounts with EUR currency
    assert "| Assets:Bank:Checking     |         1,884.65 EUR |" in table_output
    assert "| Assets:Cash:Pocket-Money |           -20.00 EUR |" in table_output
    assert "| Equity:Opening-Balances  |        -1,000.00 EUR |" in table_output
    assert "| Expenses:Sweets          |            20.00 EUR |" in table_output
    assert "| Income:Salary            |        -1,000.00 EUR |" in table_output
    
    # Should show accounts with BAM currency
    assert "| Assets:Cash:BAM          |           -25.00 BAM |" in table_output
    
    # Should show accounts with both currencies
    assert "| Expenses:Food            | 100.00 EUR 25.00 BAM |" in table_output
    
    # Should not show accounts with only ABC currency
    assert "| Equity:Stocks | 12.00 ABC |" not in table_output


@patch('os.getenv')
def test_reg_multiple_currency_filter(mock_getenv):
    """Test register command with multiple currency filter."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    # Act
    result = run_reg_command(['--currency', 'eur,abc'])

    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The query should use IN clause for multiple currencies
    assert "currency IN ('EUR', 'ABC')" in output
    
    # Should show transactions with EUR or ABC currency
    assert "EUR" in output
    assert "ABC" in output
    assert "Assets:Bank:Checking" in output
    assert "Equity:Stocks" in output