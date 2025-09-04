"""
Tests for the Balance command with hierarchy option.
"""

from tests.test_utils import run_bal_command, extract_table_data


def test_bal_with_hierarchy():
    # Act
    result = run_bal_command(['--hierarchy'])
    
    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Check that the main accounts are present
    assert "| Assets                   |" in table_output
    assert "| Assets:Bank              |" in table_output
    assert "| Assets:Cash              |" in table_output
    assert "| Equity                   |" in table_output
    assert "| Expenses                 |" in table_output
    assert "| Income                   |" in table_output
    
    # Check that individual accounts are also present
    assert "| Assets:Bank:Bank03581    |" in table_output
    assert "| Assets:Bank:Checking     |" in table_output
    assert "| Assets:Bank:Savings      |" in table_output
    assert "| Assets:Cash:BAM          |" in table_output
    assert "| Assets:Cash:Pocket-Money |" in table_output
    assert "| Assets:Cash:USD          |" in table_output


def test_bal_with_hierarchy_and_filter():
    # Act
    result = run_bal_command(['--hierarchy', 'Assets'])
    
    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Check that Assets accounts are present
    assert "| Assets                   |" in table_output
    assert "| Assets:Bank              |" in table_output
    assert "| Assets:Cash              |" in table_output
    
    # Check that individual Assets accounts are also present
    assert "| Assets:Bank:Bank03581    |" in table_output
    assert "| Assets:Bank:Checking     |" in table_output
    assert "| Assets:Bank:Savings      |" in table_output
    assert "| Assets:Cash:BAM          |" in table_output
    assert "| Assets:Cash:Pocket-Money |" in table_output
    assert "| Assets:Cash:USD          |" in table_output
    
    # Check that other account types are not present
    assert "Equity" not in table_output
    assert "Expenses" not in table_output
    assert "Income" not in table_output


def test_bal_with_hierarchy_and_exchange():
    # Act
    result = run_bal_command(['--hierarchy', '-X', 'USD'])
    
    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Check that the main accounts are present with converted values
    assert "| Assets                   |" in table_output
    assert "| Assets:Bank              |" in table_output
    assert "| Assets:Cash              |" in table_output
    assert "| Equity                   |" in table_output
    assert "| Expenses                 |" in table_output
    assert "| Income                   |" in table_output
    
    # Check that individual accounts are also present
    assert "| Assets:Bank:Bank03581    |" in table_output
    assert "| Assets:Bank:Checking     |" in table_output
    assert "| Assets:Bank:Savings      |" in table_output
    assert "| Assets:Cash:BAM          |" in table_output
    assert "| Assets:Cash:Pocket-Money |" in table_output
    assert "| Assets:Cash:USD          |" in table_output


def test_bal_with_hierarchy_and_total():
    # Act
    result = run_bal_command(['-H', '-T'])
    
    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Check that accounts are present
    assert "| Assets                   |" in table_output
    assert "| Assets:Bank              |" in table_output
    assert "| Assets:Cash              |" in table_output
    assert "| Equity                   |" in table_output
    assert "| Expenses                 |" in table_output
    assert "| Income                   |" in table_output
    
    # Check that individual accounts are also present
    assert "| Assets:Bank:Bank03581    |" in table_output
    assert "| Assets:Bank:Checking     |" in table_output
    assert "| Assets:Bank:Savings      |" in table_output
    assert "| Assets:Cash:BAM          |" in table_output
    assert "| Assets:Cash:Pocket-Money |" in table_output
    assert "| Assets:Cash:USD          |" in table_output
    
    # Check that the total row is present
    assert "| Total                    |" in table_output


def test_bal_with_collapse_level_2():
    # Act
    result = run_bal_command(['--depth', '2'])
    
    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Check that the accounts are collapsed to level 2
    assert "| Assets:Bank             |       3,000.00 CHF 1,859.65 EUR |" in table_output
    assert "| Assets:Cash             | -25.00 BAM -20.00 EUR -7.00 USD |" in table_output
    assert "| Equity:Opening-Balances |                   -1,000.00 EUR |" in table_output
    assert "| Equity:Stocks           |                       12.00 ABC |" in table_output
    assert "| Expenses:Food           |            100.00 EUR 25.00 BAM |" in table_output
    assert "| Expenses:Sweets         |                       20.00 EUR |" in table_output
    assert "| Expenses:Transport      |              7.00 USD 25.00 EUR |" in table_output
    assert "| Income:Other            |                   -3,000.00 CHF |" in table_output
    assert "| Income:Salary           |                   -1,000.00 EUR |" in table_output
    
    # Check that individual bank accounts are not present (they should be collapsed)
    assert "Assets:Bank:Checking" not in table_output
    assert "Assets:Bank:Savings" not in table_output
    assert "Assets:Bank:Bank03581" not in table_output


def test_bal_with_collapse_level_1():
    # Act
    result = run_bal_command(['--depth', '1'])
    
    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Check that the accounts are collapsed to level 1
    assert "| Assets    | 3,000.00 CHF 1,839.65 EUR -25.00 BAM -7.00 USD |" in table_output
    assert "| Equity    |                        -1,000.00 EUR 12.00 ABC |" in table_output
    assert "| Expenses  |                  145.00 EUR 25.00 BAM 7.00 USD |" in table_output
    assert "| Income    |                    -3,000.00 CHF -1,000.00 EUR |" in table_output
    
    # Check that individual accounts are not present (they should be collapsed)
    assert "Assets:Bank:Checking" not in table_output
    assert "Assets:Cash:Pocket-Money" not in table_output
    assert "Expenses:Sweets" not in table_output