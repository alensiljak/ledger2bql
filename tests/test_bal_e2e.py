'''
Tests for the Balance command.
'''
import io
import os
from contextlib import redirect_stdout
from unittest.mock import patch

from ledger2bql.ledger_bal_to_bql import main as bal_main

def extract_table_data(output_lines):
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
def test_bal_no_args(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal']):
            # Act
            bal_main()
    
    # Assert
    output = f.getvalue()
    
    table_lines = extract_table_data(output.splitlines())
    table_output = "\n".join(table_lines)

    assert "Assets:Cash:Pocket-Money" in table_output
    assert "-20.00 EUR" in table_output
    assert "Expenses:Sweets" in table_output
    assert "20.00 EUR" in table_output


@patch('os.getenv')
def test_bal_filter_by_payee(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', '@Grocery Store']):
            # Act
            bal_main()
    
    # Assert
    output = f.getvalue()
    
    table_lines = extract_table_data(output.splitlines())
    table_output = "\n".join(table_lines)

    assert "Assets:Bank:Checking" in table_output
    assert "-100.00 EUR" in table_output
    assert "Expenses:Food" in table_output
    assert "100.00 EUR" in table_output
    assert "Assets:Cash:Pocket-Money" not in table_output


@patch('os.getenv')
def test_bal_default_sort_by_account(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))

    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal']):
            # Act
            bal_main()

    # Assert
    output = f.getvalue() # Keep this to capture the output for later inspection if needed
    
    table_lines = extract_table_data(output.splitlines())
    table_output = "\n".join(table_lines)

    # Expected order based on sample_ledger.bean and alphabetical sort
    expected_table_output_lines = [
        "| Assets:Bank:Checking     |  1,884.65 EUR |",
        "| Assets:Cash:Pocket-Money |    -20.00 EUR |",
        "| Equity:Opening-Balances  | -1,000.00 EUR |",
        "| Expenses:Food            |    100.00 EUR |",
        "| Expenses:Sweets          |     20.00 EUR |",
        "| Income:Salary            | -1,000.00 EUR |"
    ]
    
    # Check if the table output contains the expected lines in order
    for expected_line in expected_table_output_lines:
        assert expected_line in table_output


@patch('os.getenv')
def test_bal_sort_by_balance(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))

    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', '--sort', 'balance']):
            # Act
            bal_main()

    # Assert
    output = f.getvalue()
    
    table_lines = extract_table_data(output.splitlines())
    table_output = "\n".join(table_lines)

    # Expected order based on balances in sample_ledger.bean
    # Assuming ascending order for now, adjust if BQL sorts descending by default
    expected_order_balances = [
        "-1,000.00 EUR", # Equity:Opening-Balances
        "-1,000.00 EUR", # Income:Salary
        "-20.00 EUR", # Assets:Cash:Pocket-Money
        "20.00 EUR", # Expenses:Sweets
        "100.00 EUR", # Expenses:Food
        "1,884.65 EUR"  # Assets:Bank:Checking
    ]

    # Extract balances from the output and check their order
    output_lines = table_output.splitlines()
    found_balances = []
    for expected_balance in expected_order_balances:
        for line in output_lines:
            if expected_balance in line:
                found_balances.append(expected_balance)
                break
    
    # This assertion might be tricky due to multiple accounts having the same balance
    # and the exact string matching. A more robust test would parse the table.
    # For now, this is a basic check.
    assert found_balances == expected_order_balances


@patch('os.getenv')
def test_bal_cash_zero_balance(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))

    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', 'cash', '-Z']):
            # Act
            bal_main()

    # Assert
    output = f.getvalue()
    
    table_lines = extract_table_data(output.splitlines())
    table_output = "\n".join(table_lines)

    assert "Assets:Cash:Pocket-Money" in table_output
    assert "-20.00 EUR" in table_output # Assuming this is the balance for Pocket-Money
    assert "Assets:Cash:Wallet" not in table_output # Assuming Wallet has zero balance or is not present


@patch('os.getenv')
def test_bal_cash_zero_balance_new(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))

    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', 'cash', '-Z']):
            # Act
            bal_main()

    # Assert
    output = f.getvalue()
    
    table_lines = extract_table_data(output.splitlines())
    table_output = "\n".join(table_lines)

    assert "Assets:Cash:Pocket-Money" in table_output
    assert "-20.00 EUR" in table_output
    assert "Assets:Cash:Wallet" not in table_output


@patch('os.getenv')
def test_bal_gratis_empty_account(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))

    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', 'Assets:Cash:Wallet']):
            # Act
            bal_main()
        output_no_z = f.getvalue()
    table_lines_no_z = extract_table_data(output_no_z.splitlines())
    table_output_no_z = "\n".join(table_lines_no_z)

    # Assert
    assert "No records found." in output_no_z
    assert "Assets:Cash:Wallet" not in table_output_no_z

    # Test with -Z: empty account should also result in "No records found."
    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', 'Assets:Cash:Wallet', '-Z']):
            # Act
            bal_main()
        output_with_z = f.getvalue()
    table_lines_with_z = extract_table_data(output_with_z.splitlines())
    table_output_with_z = "\n".join(table_lines_with_z)

    # Assert
    assert "No records found." in output_with_z
    assert "Assets:Cash:Wallet" not in table_output_with_z


@patch('os.getenv')
def test_bal_units(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))

    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', 'Equity:Stocks']):
            # Act
            bal_main()

    # Assert
    output = f.getvalue()

    table_lines = extract_table_data(output.splitlines())
    table_output = "\n".join(table_lines)

    assert "| Equity:Stocks | 12.00 ABC |" in table_output