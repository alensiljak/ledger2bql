"""
Tests for the currency parameter functionality.
"""
import io
import os
from contextlib import redirect_stdout
from unittest.mock import patch

from ledger2bql.ledger_bal_to_bql import main as bal_main
from ledger2bql.ledger_reg_to_bql import main as reg_main


def extract_table_data(output_lines):
    """Extract table data from output lines."""
    table_data = []
    start_index = -1
    end_index = -1

    for i, line in enumerate(output_lines):
        if line.strip().startswith("+") and "---" in line:
            if start_index == -1:
                start_index = i
            else:
                end_index = i
                break
    
    if start_index != -1 and end_index != -1:
        # The actual data starts after the header and separator lines
        for line in output_lines[start_index + 3:end_index]:
            table_data.append(line)
    
    return table_data


@patch('os.getenv')
def test_bal_currency_filter_eur(mock_getenv):
    """Test balance command with EUR currency filter."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', '--currency', 'eur']):
            # Act
            bal_main()

    # Assert
    output = f.getvalue()
    
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

    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', '--currency', 'bam']):
            # Act
            bal_main()

    # Assert
    output = f.getvalue()
    
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

    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', '--currency', 'abc']):
            # Act
            bal_main()

    # Assert
    output = f.getvalue()
    
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

    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['reg', '--currency', 'abc']):
            # Act
            reg_main()

    # Assert
    output = f.getvalue()
    
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
    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', '-c', 'eur']):
            # Act
            bal_main()

    # Assert - the query should use uppercase currency
    output = f.getvalue()
    assert "currency = 'EUR'" in output
    assert "currency = 'eur'" not in output

    # Test with mixed case currency that exists in the ledger
    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', '-c', 'AbC']):
            # Act
            bal_main()

    # Assert - the query should use uppercase currency
    output = f.getvalue()
    assert "currency = 'ABC'" in output
    assert "currency = 'AbC'" not in output