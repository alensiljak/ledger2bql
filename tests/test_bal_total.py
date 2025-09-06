"""
Tests for the Balance command with total option.
"""

from tests.test_utils import run_bal_command, extract_table_data


def test_bal_with_total():
    # Act
    result = run_bal_command(["--total"])

    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Check that the total row is present
    assert "| Total" in table_output

    # Check that some expected accounts are still present
    assert "Assets:Bank:Checking" in table_output
    assert "Expenses:Sweets" in table_output

    # Check that the separator row is NOT present (it should be filtered out)
    assert "| ------------------- | ------------------- |" not in table_output


def test_bal_with_total_flag_short():
    # Act
    result = run_bal_command(["-T"])

    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Check that the total row is present
    assert "| Total" in table_output

    # Check that some expected accounts are still present
    assert "Assets:Bank:Checking" in table_output
    assert "Expenses:Sweets" in table_output

    # Check that the separator row is NOT present (it should be filtered out)
    assert "| ------------------- | ------------------- |" not in table_output
