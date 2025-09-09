"""
Tests for the Lots command.
"""

import pytest
from tests.test_utils import run_lots_command, extract_table_data


def test_lots_no_args():
    # Act
    result = run_lots_command()

    # Assert
    assert result.exit_code == 0
    assert "SELECT date, account, currency(units(position)) as symbol, units(position) as quantity, cost_number as cost" in result.output
    assert "cost_number IS NOT NULL" in result.output

    # Check that the output contains the expected lots from sample_ledger.bean
    # Based on the sample ledger, we should see ABC lots
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Should contain the ABC lots from the sample ledger
    assert "Equity:Stocks" in table_output
    assert "ABC" in table_output  # The symbol is ABC, not EUR
    assert "5" in table_output  # First lot (shown as integer)
    assert "7" in table_output  # Second lot (shown as integer)
    assert "1.25" in table_output  # First cost
    assert "1.30" in table_output  # Second cost
    # Check that costs are displayed with the cost currency (EUR)
    assert "1.25 EUR" in table_output
    assert "1.30 EUR" in table_output


def test_lots_filter_by_account():
    # Act
    result = run_lots_command(["Equity"])

    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Should only show lots from Equity accounts
    assert "Equity:Stocks" in table_output
    assert "ABC" in table_output
    assert "Assets:Bank:Checking" not in table_output  # This is not an Equity account


@pytest.mark.skip(reason="avg() function not working with decimal types in BQL")
def test_lots_average():
    # Act
    result = run_lots_command(["--average"])

    # Assert
    assert result.exit_code == 0
    assert "SELECT date, account, currency(units(position)) as symbol, sum(units(position)) as quantity, avg(cost_number) as avg_cost" in result.output
    
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Should show average costs
    assert "Equity:Stocks" in table_output
    assert "ABC" in table_output
    # Average cost should be (5*1.25 + 7*1.30) / (5+7) = (6.25 + 9.1) / 12 = 15.35 / 12 = 1.279...
    # So we should see 12.00 quantity and around 1.28 cost
    assert "12.00" in table_output


def test_lots_sort_by_date():
    # Act
    result = run_lots_command(["--sort-by", "date"])

    # Assert
    assert result.exit_code == 0
    assert "ORDER BY date ASC" in result.output


def test_lots_sort_by_price():
    # Act
    result = run_lots_command(["--sort-by", "price"])

    # Assert
    assert result.exit_code == 0
    assert "ORDER BY cost_number ASC" in result.output


def test_lots_sort_by_symbol():
    # Act
    result = run_lots_command(["--sort-by", "symbol"])

    # Assert
    assert result.exit_code == 0
    assert "ORDER BY symbol ASC" in result.output
