"""
A command-line tool to translate ledger-cli 'lots' command syntax
into a Beanquery (BQL) query.
"""

import click
from decimal import Decimal
from .date_parser import parse_date, parse_date_range
from .utils import (
    add_common_click_arguments,
    execute_bql_command_with_click,
    parse_account_params,
    parse_account_pattern,
    parse_amount_filter,
)


@click.command(name="lots", short_help="[l] Show investment lots")
@click.option(
    "--sort-by",
    "-s",
    type=click.Choice(["date", "price", "symbol"]),
    help="Sort lots by date, price, or symbol.",
)
@click.option(
    "--average",
    "-A",
    is_flag=True,
    help="Show average cost for each symbol.",
)
@click.option(
    "--active",
    is_flag=True,
    help="Show only active/open lots (default).",
)
@click.option(
    "--all",
    "show_all",
    is_flag=True,
    help="Show all lots, including sold ones.",
)
@click.argument("account_regex", nargs=-1)
@add_common_click_arguments
def lots_command(account_regex, sort_by, average, active, show_all, **kwargs):
    """Translate ledger-cli lots command arguments to a Beanquery (BQL) query."""

    # Package arguments in a way compatible with the existing code
    class Args:
        def __init__(self, account_regex, sort_by, average, active, show_all, **kwargs):
            self.account_regex = account_regex
            self.sort_by = sort_by
            self.average = average
            self.active = active
            self.show_all = show_all
            for key, value in kwargs.items():
                setattr(self, key, value)

    args = Args(account_regex, sort_by, average, active, show_all, **kwargs)

    # Determine headers for the table
    if average:
        headers = [
            "Date",
            "Account",
            "Quantity",
            "Symbol",
            "Average Price",
            "Total Cost",
            "Value",
        ]
        alignments = ["left", "left", "right", "left", "right", "right", "right"]
    else:
        headers = ["Date", "Account", "Quantity", "Symbol", "Price", "Cost", "Value"]
        alignments = ["left", "left", "right", "left", "right", "right", "right"]

    # Execute the command
    execute_bql_command_with_click(
        parse_query, format_output, headers, alignments, args, command_type="lots"
    )


def parse_query(args):
    """Parse Ledger query into BQL"""
    where_clauses = []
    group_by_clauses = []

    # Handle account regular expressions and payee filters
    account_regexes, excluded_account_regexes, payee_where_clauses = (
        parse_account_params(args.account_regex)
    )
    where_clauses.extend(payee_where_clauses)

    if account_regexes:
        for pattern in account_regexes:
            regex_pattern = parse_account_pattern(pattern)
            where_clauses.append(f"account ~ '{regex_pattern}'")

    if excluded_account_regexes:
        for pattern in excluded_account_regexes:
            regex_pattern = parse_account_pattern(pattern)
            where_clauses.append(f"NOT (account ~ '{regex_pattern}')")

    # Handle date ranges
    if hasattr(args, "begin") and args.begin:
        begin_date = parse_date(args.begin)
        where_clauses.append(f'date >= date("{begin_date}")')
    if hasattr(args, "end") and args.end:
        end_date = parse_date(args.end)
        where_clauses.append(f'date < date("{end_date}")')

    # Handle date range if provided
    if hasattr(args, "date_range") and args.date_range:
        begin_date, end_date = parse_date_range(args.date_range)
        if begin_date:
            where_clauses.append(f'date >= date("{begin_date}")')
        if end_date:
            where_clauses.append(f'date < date("{end_date}")')

    # Handle amount filters
    if hasattr(args, "amount") and args.amount:
        for amount_filter in args.amount:
            op, val, cur = parse_amount_filter(amount_filter)
            amount_clause = f"number {op} {val}"
            if cur:
                amount_clause += f" AND currency = '{cur}'"
            where_clauses.append(amount_clause)

    # Handle currency filter
    if hasattr(args, "currency") and args.currency:
        if isinstance(args.currency, list):
            currencies_str = "', '".join(args.currency)
            where_clauses.append(f"currency IN ('{currencies_str}')")
        else:
            where_clauses.append(f"currency = '{args.currency}'")

    # Build the final query for lots
    # We need to select lots information from positions that have cost basis
    if args.average:
        # For average cost, we'll use GROUP BY and aggregate functions in SQL
        select_clause = "SELECT MAX(date) as date, account, currency(units(position)) as symbol, SUM(units(position)) as quantity, SUM(cost_number * number(units(position))) / SUM(number(units(position))) as avg_price, cost(SUM(position)) as total_cost, value(SUM(position)) as value"
        where_clauses.append(
            "cost_number IS NOT NULL"
        )  # Only positions with cost basis

        query = select_clause

        # Add GROUP BY for average cost calculation
        group_by_clauses = ["account", "currency(units(position))"]
    else:
        # For detailed lots
        if args.show_all:
            # Show all individual lots (buys and sells) - original behavior
            select_clause = "SELECT date, account, currency(units(position)) as symbol, units(position) as quantity, cost_number as price, cost(position) as cost, value(position) as value"
            where_clauses.append(
                "cost_number IS NOT NULL"
            )  # Only positions with cost basis
            group_by_clauses = []  # No grouping
        else:
            # Show aggregated active lots only
            select_clause = "SELECT MAX(date) as date, account, currency(units(position)) as symbol, SUM(units(position)) as quantity, cost_number as price, cost(SUM(position)) as cost, value(SUM(position)) as value"
            where_clauses.append(
                "cost_number IS NOT NULL"
            )  # Only positions with cost basis
            # Group by lot identifiers
            group_by_clauses = [
                "account",
                "currency(units(position))",
                "cost_number",
                "cost_currency",
            ]

        query = select_clause

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    if group_by_clauses:
        query += " GROUP BY " + ", ".join(group_by_clauses)

        # Filter for active lots if not showing all
        if not args.show_all:
            query += " HAVING SUM(number(units(position))) > 0"

    # Handle sorting
    if args.average:
        # Handle sorting for average case
        if hasattr(args, "sort") and args.sort:
            sort_fields = []
            for field in args.sort.split(","):
                field = field.strip()
                sort_order = "ASC"
                if field.startswith("-"):
                    field = field[1:]
                    sort_order = "DESC"

                # Map field names to appropriate BQL fields
                if field == "balance":
                    sort_fields.append(f"sum(position) {sort_order}")
                else:
                    sort_fields.append(f"{field} {sort_order}")
            query += " ORDER BY " + ", ".join(sort_fields)
        elif args.sort_by:
            # Handle specific sort options from --sort-by
            sort_mapping = {"date": "date", "price": "avg_price", "symbol": "symbol"}
            if args.sort_by in sort_mapping:
                query += f" ORDER BY {sort_mapping[args.sort_by]} ASC"
        else:
            # Default sorting by date
            query += " ORDER BY date ASC"
    else:
        # Handle sorting for detailed lots
        if hasattr(args, "sort") and args.sort:
            sort_fields = []
            for field in args.sort.split(","):
                field = field.strip()
                sort_order = "ASC"
                if field.startswith("-"):
                    field = field[1:]
                    sort_order = "DESC"

                # Map field names to appropriate BQL fields
                if field == "balance":
                    sort_fields.append(f"sum(position) {sort_order}")
                else:
                    sort_fields.append(f"{field} {sort_order}")
            query += " ORDER BY " + ", ".join(sort_fields)
        elif args.sort_by:
            # Handle specific sort options from --sort-by
            sort_mapping = {"date": "date", "price": "price", "symbol": "symbol"}
            if args.sort_by in sort_mapping:
                query += f" ORDER BY {sort_mapping[args.sort_by]} ASC"
        else:
            # Default sorting by date
            query += " ORDER BY date ASC"

    # Handle limit
    if hasattr(args, "limit") and args.limit:
        query += f" LIMIT {args.limit}"

    return query


def format_output(output: list, args) -> list:
    """Formats the raw output from the BQL query into a pretty-printable list."""
    formatted_output = []

    if args.average:
        # For average cost, we receive aggregated data from SQL
        for row in output:
            # For average lots: date, account, symbol, quantity, avg_price, total_cost, value
            date, account, symbol, quantity, avg_price, total_cost, value = row

            # Extract the number from the Amount object for quantity
            if hasattr(quantity, "get_positions"):
                # This is an Inventory object
                positions = quantity.get_positions()
                if positions:
                    quantity_number = positions[0].units.number
                else:
                    quantity_number = Decimal("0")
            elif hasattr(quantity, "units") and hasattr(quantity.units, "number"):
                # This is a Position object with units
                quantity_number = quantity.units.number
            elif hasattr(quantity, "number"):
                # This is already an Amount object
                quantity_number = quantity.number
            else:
                # Try to convert to Decimal directly
                quantity_number = (
                    Decimal(str(quantity)) if quantity is not None else Decimal("0")
                )

            # Extract the average price
            avg_price_decimal = (
                Decimal(str(avg_price)) if avg_price is not None else Decimal("0")
            )

            # Extract the total cost
            total_cost_decimal = Decimal("0")
            cost_currency = symbol  # Default to symbol as currency
            if hasattr(total_cost, "get_positions"):
                # This is an Inventory object
                positions = total_cost.get_positions()
                if positions:
                    pos = positions[0]
                    total_cost_decimal = pos.units.number
                    cost_currency = (
                        pos.units.currency
                    )  # Update cost_currency from the actual cost object
            elif hasattr(total_cost, "number"):
                # This is already an Amount object
                total_cost_decimal = total_cost.number
                if hasattr(total_cost, "currency"):
                    cost_currency = total_cost.currency
            elif total_cost is not None:
                # Try to convert to Decimal directly
                total_cost_decimal = (
                    Decimal(str(total_cost)) if total_cost is not None else Decimal("0")
                )

            # Format the output
            formatted_quantity = "{:,.2f}".format(quantity_number)
            formatted_avg_price = "{:,.2f} {}".format(avg_price_decimal, cost_currency)
            formatted_total_cost = "{:,.2f} {}".format(
                total_cost_decimal, cost_currency
            )

            # Format the value
            value_str = ""
            if hasattr(value, "get_positions"):
                # This is an Inventory object
                positions = value.get_positions()
                if positions:
                    pos = positions[0]
                    value_number = pos.units.number
                    value_currency = pos.units.currency
                    value_str = "{:,.2f} {}".format(value_number, value_currency)
            elif hasattr(value, "number") and hasattr(value, "currency"):
                value_number = value.number
                value_currency = value.currency
                value_str = "{:,.2f} {}".format(value_number, value_currency)
            elif (
                hasattr(value, "units")
                and hasattr(value.units, "number")
                and hasattr(value.units, "currency")
            ):
                # Position object with units
                value_number = value.units.number
                value_currency = value.units.currency
                value_str = "{:,.2f} {}".format(value_number, value_currency)
            elif value is not None:
                # Try to convert to string directly and format properly
                value_str = str(value)
                # If it's in the format "(16.20 EUR)", extract the number and currency
                import re

                match = re.match(r"$(\d+\.?\d*)\s+([A-Z]{3})$", value_str)
                if match:
                    value_str = "{} {}".format(match.group(1), match.group(2))

            formatted_output.append(
                [
                    str(date),
                    account,
                    formatted_quantity,
                    symbol,
                    formatted_avg_price,
                    formatted_total_cost,
                    value_str,
                ]
            )
    else:
        # For detailed lots
        for row in output:
            # For detailed lots: date, account, symbol, quantity, price, cost, value
            date, account, symbol, quantity, price, cost, value = row

            # Extract the number from the Amount object for quantity
            quantity_number = Decimal("0")
            if hasattr(quantity, "get_positions"):
                # This is an Inventory object - for individual positions, get the first position
                positions = quantity.get_positions()
                if positions:
                    quantity_number = positions[0].units.number
            elif hasattr(quantity, "units") and hasattr(quantity.units, "number"):
                # This is a Position object with units
                quantity_number = quantity.units.number
            elif hasattr(quantity, "number"):
                # This is already an Amount object
                quantity_number = quantity.number
            elif quantity is not None:
                # Try to convert to Decimal directly
                quantity_number = Decimal(str(quantity))

            price_decimal = Decimal("0")
            if price is not None:
                price_decimal = Decimal(str(price))

            # Format the cost
            # cost is already a Beancount Amount object with number and currency
            cost_str = ""
            if hasattr(cost, "get_positions"):
                # This is an Inventory object - extract the cost
                positions = cost.get_positions()
                if positions:
                    pos = positions[0]
                    cost_number = pos.units.number
                    cost_currency = pos.units.currency
                    cost_str = f"{cost_number} {cost_currency}"
            elif hasattr(cost, "number") and hasattr(cost, "currency"):
                cost_number = cost.number
                cost_currency = cost.currency
                cost_str = f"{cost_number} {cost_currency}"
            elif (
                hasattr(cost, "units")
                and hasattr(cost.units, "number")
                and hasattr(cost.units, "currency")
            ):
                # Position object with units
                cost_number = cost.units.number
                cost_currency = cost.units.currency
                cost_str = f"{cost_number} {cost_currency}"
            elif cost is not None:
                cost_str = str(cost)

            # Format the value
            # value is already a Beancount Amount object with number and currency
            value_str = ""
            if hasattr(value, "get_positions"):
                # This is an Inventory object - extract the value
                positions = value.get_positions()
                if positions:
                    pos = positions[0]
                    value_number = pos.units.number
                    value_currency = pos.units.currency
                    value_str = "{:,.2f} {}".format(value_number, value_currency)
            elif hasattr(value, "number") and hasattr(value, "currency"):
                value_number = value.number
                value_currency = value.currency
                value_str = "{:,.2f} {}".format(value_number, value_currency)
            elif (
                hasattr(value, "units")
                and hasattr(value.units, "number")
                and hasattr(value.units, "currency")
            ):
                # Position object with units
                value_number = value.units.number
                value_currency = value.units.currency
                value_str = "{:,.2f} {}".format(value_number, value_currency)
            elif value is not None:
                value_str = str(value)

            formatted_quantity = "{:,}".format(
                int(quantity_number)
                if quantity_number == int(quantity_number)
                else quantity_number
            )  # Show as integer if whole number
            formatted_price = "{:,.2f} {}".format(
                price_decimal,
                # Extract currency from cost if available
                cost.currency
                if hasattr(cost, "currency")
                else (cost_currency if "cost_currency" in locals() else ""),
            )
            formatted_output.append(
                [
                    str(date),
                    account,
                    formatted_quantity,
                    symbol,
                    formatted_price,
                    cost_str,
                    value_str,
                ]
            )

    return formatted_output
