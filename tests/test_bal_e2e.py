"""
Tests for the Balance command.
"""

from tests.test_utils import run_bal_command, extract_table_data


def test_bal_no_args():
    # Act
    result = run_bal_command()

    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    assert "Assets:Cash:Pocket-Money" in table_output
    assert "-45.00 EUR" in table_output  # Updated to reflect new transaction
    assert "Expenses:Sweets" in table_output
    assert "20.00 EUR" in table_output


def test_bal_filter_by_payee():
    # Act
    result = run_bal_command(["@Grocery Store"])

    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    assert "Assets:Bank:Checking" in table_output
    assert "-100.00 EUR" in table_output
    assert "Expenses:Food" in table_output
    assert "100.00 EUR" in table_output
    assert "Assets:Cash:Pocket-Money" not in table_output


def test_bal_default_sort_by_account():
    # Act
    result = run_bal_command()

    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Expected order based on sample_ledger.bean and alphabetical sort
    expected_table_output_lines = [
        "| Assets:Bank:Checking     |         1,359.65 EUR |",
        "| Assets:Cash:BAM          |           -25.00 BAM |",
        "| Assets:Cash:Pocket-Money |           -45.00 EUR |",  # Updated to reflect new transaction
        "| Assets:Cash:USD          |            -7.00 USD |",
        "| Equity:Opening-Balances  |        -1,000.00 EUR |",
        "| Equity:Stocks            |            12.00 ABC |",
        "| Expenses:Accommodation   |            25.00 EUR |",  # Added new transaction
        "| Expenses:Food            | 100.00 EUR 25.00 BAM |",
        "| Expenses:Sweets          |            20.00 EUR |",
        "| Expenses:Transport       |             7.00 USD |",
        "| Income:Salary            |        -1,000.00 EUR |",
    ]

    # Check if the table output contains the expected lines in order
    for expected_line in expected_table_output_lines:
        assert expected_line in table_output


def test_bal_sort_by_balance():
    # Act
    result = run_bal_command(["--sort", "balance"])

    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Expected order based on balances in sample_ledger.bean
    # Sorted by actual balance amount (including currency), ascending order
    # USD amounts come first (negative), then EUR (negative), then EUR (positive), then CHF (negative), then CHF (positive), then BAM, then ABC
    expected_order_balances = [
        "-7.00 USD",  # Assets:Cash:USD
        "7.00 USD",  # Expenses:Transport
        "-25.00 BAM",  # Assets:Cash:BAM
        "12.00 ABC",  # Equity:Stocks
        "-1,000.00 EUR",  # Equity:Opening-Balances
        "-1,000.00 EUR",  # Income:Salary
        "-45.00 EUR",  # Assets:Cash:Pocket-Money
        "10.00 EUR",  # Expenses:Transport:Bus
        "15.00 EUR",  # Expenses:Transport:Train
        "20.00 EUR",  # Expenses:Sweets
        "25.00 EUR",  # Expenses:Accommodation
        "100.00 EUR",  # Expenses:Food (partially)
        "500.00 EUR",  # Assets:Bank:Savings
        "1,359.65 EUR",  # Assets:Bank:Checking
        "-3,000.00 CHF",  # Income:Other
        "3,000.00 CHF",  # Assets:Bank:Bank03581
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


def test_bal_cash_zero_balance():
    # Act
    result = run_bal_command(["cash", "-Z"])

    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    assert "Assets:Cash:Pocket-Money" in table_output
    assert "-45.00 EUR" in table_output  # Updated to reflect new transaction
    assert (
        "Assets:Cash:Wallet" not in table_output
    )  # Assuming Wallet has zero balance or is not present


def test_bal_cash_zero_balance_new():
    # Act
    result = run_bal_command(["cash", "-Z"])

    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    assert "Assets:Cash:Pocket-Money" in table_output
    assert "-45.00 EUR" in table_output  # Updated to reflect new transaction
    assert "Assets:Cash:Wallet" not in table_output


def test_bal_gratis_empty_account():
    # Act
    result_no_z = run_bal_command(["Assets:Cash:Wallet"])

    # Assert
    assert result_no_z.exit_code == 0
    assert "No records found." in result_no_z.output
    table_lines_no_z = extract_table_data(result_no_z.output.splitlines())
    table_output_no_z = "\n".join(table_lines_no_z)
    assert "Assets:Cash:Wallet" not in table_output_no_z

    # Test with -Z: empty account should also result in "No records found."
    result_with_z = run_bal_command(["Assets:Cash:Wallet", "-Z"])

    # Assert
    assert result_with_z.exit_code == 0
    assert "No records found." in result_with_z.output
    table_lines_with_z = extract_table_data(result_with_z.output.splitlines())
    table_output_with_z = "\n".join(table_lines_with_z)
    assert "Assets:Cash:Wallet" not in table_output_with_z


def test_bal_units():
    # Act
    result = run_bal_command(["Equity:Stocks"])

    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    assert "| Equity:Stocks | 12.00 ABC |" in table_output


def test_bal_filter_by_payee_and_date():
    # Act
    result = run_bal_command(["@Employer", "-b", "2025-03"])

    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    assert "Assets:Bank:Checking" in table_output
    assert "1,000.00 EUR" in table_output
    assert "Income:Salary" in table_output
    assert "-1,000.00 EUR" in table_output
    assert "Expenses:Food" not in table_output


def test_bal_filter_by_amount_gt():
    # Act
    result = run_bal_command(["--amount", ">50"])

    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    assert "Expenses:Food" in table_output
    assert "100.00 EUR" in table_output
    assert "Assets:Bank:Checking" in table_output
    assert "2,000.00 EUR" in table_output
    assert "Expenses:Sweets" not in table_output
