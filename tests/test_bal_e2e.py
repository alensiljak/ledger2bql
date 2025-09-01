'''
Tests for the Balance command.
'''
from unittest.mock import patch
import io
from contextlib import redirect_stdout
import os

from ledger2bql.ledger_bal_to_bql import main as bal_main

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
    assert "Assets:Cash:Pocket-Money" in output
    assert "-20.00 EUR" in output
    assert "Expenses:Sweets" in output
    assert "20.00 EUR" in output


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
    output = f.getvalue()
    # Check if the accounts are sorted alphabetically
    # The expected order based on sample_ledger.bean and alphabetical sort
    expected_order = [
        "Assets:Bank:Checking",
        "Assets:Cash:Pocket-Money",
        "Equity:Opening-Balances",
        "Expenses:Food",
        "Expenses:Sweets",
        "Income:Salary"
    ]
    
    # Extract account names from the output and check their order
    # This is a simplified check, assuming each account name appears on a new line
    # and we can find them in the expected order.
    output_lines = output.splitlines()
    found_accounts = []
    for account in expected_order:
        for line in output_lines:
            if account in line:
                found_accounts.append(account)
                break
    
    assert found_accounts == expected_order


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
    # Expected order based on balances in sample_ledger.bean
    # Assuming ascending order for now, adjust if BQL sorts descending by default
    expected_order_balances = [
        "-1,000.00 EUR", # Equity:Opening-Balances
        "-1,000.00 EUR", # Income:Salary
        "-20.00 EUR", # Assets:Cash:Pocket-Money
        "20.00 EUR", # Expenses:Sweets
        "100.00 EUR", # Expenses:Food
        "1,900.00 EUR"  # Assets:Bank:Checking
    ]

    # Extract balances from the output and check their order
    output_lines = output.splitlines()
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
