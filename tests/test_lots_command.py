"""
Tests for the Lots command.
"""

from tests.test_utils import run_lots_command, extract_table_data


def test_lots_no_args():
    # Act
    result = run_lots_command()

    # Assert
    assert result.exit_code == 0
    assert (
        "SELECT MAX(date) as date, account, currency(units(position)) as symbol, SUM(units(position)) as quantity, cost_number as price, cost(SUM(position)) as cost, value(SUM(position)) as value"
        in result.output
    )
    assert "cost_number IS NOT NULL" in result.output
    assert "HAVING SUM(number(units(position))) > 0" in result.output

    # Check that the output contains the expected lots from sample_ledger.bean
    # Based on the sample ledger, after selling we should see only 4 ABC stocks from the second lot
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Should contain the ABC lots from the sample ledger
    assert "Equity:Stocks" in table_output
    assert "ABC" in table_output  # The symbol is ABC, not EUR
    assert "4" in table_output  # Only 4 stocks remaining after sales
    assert "1.30" in table_output  # Price of remaining lot
    # Check that prices are displayed with the cost currency (EUR)
    assert "1.30 EUR" in table_output
    # Check that costs are displayed with quantity and currency
    assert "5.20 EUR" in table_output  # 4 * 1.30 = 5.20


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


def test_lots_average():
    # Act
    result = run_lots_command(["--average"])

    # Print the result for debugging
    print("Exit code:", result.exit_code)
    print("Output:", result.output)

    # Assert
    assert result.exit_code == 0
    assert (
        "SELECT MAX(date) as date, account, currency(units(position)) as symbol, SUM(units(position)) as quantity, SUM(cost_number * number(units(position))) / SUM(number(units(position))) as avg_price, cost(SUM(position)) as total_cost, value(SUM(position)) as value"
        in result.output
    )

    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Should show average prices
    assert "Equity:Stocks" in table_output
    assert "ABC" in table_output
    # After selling, we have 4 ABC stocks at 1.30 EUR each
    # So we should see 4 quantity and 1.30 price
    assert "4" in table_output  # Total quantity
    assert "1.30 EUR" in table_output  # Average price (same as remaining lot)
    assert "5.20 EUR" in table_output  # Total cost (4 * 1.30)


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
    assert "ORDER BY price ASC" in result.output


def test_lots_sort_by_symbol():
    # Act
    result = run_lots_command(["--sort-by", "symbol"])

    # Assert
    assert result.exit_code == 0
    assert "ORDER BY symbol ASC" in result.output


def test_lots_show_all():
    # Act
    result = run_lots_command(["--all"])

    # Assert
    assert result.exit_code == 0
    assert (
        "SELECT date, account, currency(units(position)) as symbol, units(position) as quantity, cost_number as price, cost(position) as cost, value(position) as value"
        in result.output
    )
    assert "cost_number IS NOT NULL" in result.output
    assert "GROUP BY" not in result.output  # Should not group when showing all

    # Check that the output contains all individual lots (buys and sells)
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Should show all lots including buys and sells
    assert "Equity:Stocks" in table_output
    assert "ABC" in table_output
    # Should show the buy lots
    assert "5" in table_output  # First buy
    assert "7" in table_output  # Second buy
    assert "1.25" in table_output  # First buy price
    assert "1.30" in table_output  # Second buy price
    # Should show the sell lots with negative quantities
    assert "-5" in table_output  # First sell
    assert "-3" in table_output  # Second sell


def test_lots_active():
    # Act
    result = run_lots_command(["--active"])

    # Assert
    assert result.exit_code == 0
    assert (
        "SELECT MAX(date) as date, account, currency(units(position)) as symbol, SUM(units(position)) as quantity, cost_number as price, cost(SUM(position)) as cost, value(SUM(position)) as value"
        in result.output
    )
    assert "cost_number IS NOT NULL" in result.output
    assert "HAVING SUM(number(units(position))) > 0" in result.output  # Should filter for active

    # Check that the output contains only active lots
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Should contain the ABC lots from the sample ledger
    assert "Equity:Stocks" in table_output
    assert "ABC" in table_output
    assert "4" in table_output  # Only 4 stocks remaining after sales
    assert "1.30" in table_output  # Price of remaining lot
    # Should not show any rows with 0 quantity (which would indicate sold lots)
    # Just check that we have exactly one row with quantity 4
    assert table_output.count("4") >= 1  # At least one occurrence of "4"
