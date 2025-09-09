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
    parse_amount_filter,
    parse_account_pattern,
)


@click.command(name="lots", short_help="Show investment lots")
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
@click.argument("account_regex", nargs=-1)
@add_common_click_arguments
def lots_command(account_regex, sort_by, average, **kwargs):
    """Translate ledger-cli lots command arguments to a Beanquery (BQL) query."""
    
    # Package arguments in a way compatible with the existing code
    class Args:
        def __init__(self, account_regex, sort_by, average, **kwargs):
            self.account_regex = account_regex
            self.sort_by = sort_by
            self.average = average
            for key, value in kwargs.items():
                setattr(self, key, value)

    args = Args(account_regex, sort_by, average, **kwargs)

    # Determine headers for the table
    if average:
        headers = ["Date", "Account", "Quantity", "Symbol", "Average Cost", "Total Cost"]
        alignments = ["left", "left", "right", "left", "right", "right"]
    else:
        headers = ["Date", "Account", "Quantity", "Symbol", "Cost"]
        alignments = ["left", "left", "right", "left", "right"]

    # Execute the command
    execute_bql_command_with_click(
        parse_query, format_output, headers, alignments, args, command_type="lots"
    )


def parse_query(args):
    """Parse Ledger query into BQL"""
    where_clauses = []
    account_regexes = []
    excluded_account_regexes = []

    # Handle account regular expressions and payee filters
    if args.account_regex:
        i = 0
        while i < len(args.account_regex):
            regex = args.account_regex[i]
            if regex == "not":
                # The next argument(s) should be excluded
                i += 1
                while i < len(args.account_regex):
                    next_regex = args.account_regex[i]
                    if next_regex.startswith("@") or next_regex == "not":
                        # If we encounter another @ pattern or 'not', stop excluding
                        i -= 1  # Step back to process this in the next iteration
                        break
                    else:
                        excluded_account_regexes.append(next_regex)
                        i += 1
            elif regex.startswith("@"):
                payee = regex[1:]
                where_clauses.append(f"description ~ '{payee}'")
            else:
                account_regexes.append(regex)
            i += 1

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
        # For average cost, we need to aggregate by account and commodity
        select_clause = "SELECT date, account, currency(units(position)) as symbol, sum(units(position)) as quantity, avg(cost_number) as avg_cost, sum(cost_number * units(position)) as total_cost, cost_currency"
        where_clauses.append("cost_number IS NOT NULL")  # Only positions with cost basis
        group_by_clause = "GROUP BY date, account, symbol, cost_currency"
        query = select_clause
    else:
        # For detailed lots, we need to show individual lots
        select_clause = "SELECT date, account, currency(units(position)) as symbol, units(position) as quantity, cost_number as cost, cost_currency"
        where_clauses.append("cost_number IS NOT NULL")  # Only positions with cost basis
        query = select_clause
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    # Add GROUP BY for average cost calculation
    if args.average:
        query += f" {group_by_clause}"

    # Handle sorting
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
        sort_mapping = {
            "date": "date",
            "price": "cost_number",
            "symbol": "symbol"
        }
        if args.sort_by in sort_mapping:
            query += f" ORDER BY {sort_mapping[args.sort_by]} ASC"
    else:
        # Default sorting by date
        query += " ORDER BY date ASC"

    return query


def format_output(output: list, args) -> list:
    """Formats the raw output from the BQL query into a pretty-printable list."""
    formatted_output = []

    for row in output:
        if args.average:
            # For average cost: date, account, symbol, quantity, avg_cost, total_cost, cost_currency
            date, account, symbol, quantity, avg_cost, total_cost, cost_currency = row
            # Extract the number from the Amount object
            if hasattr(quantity, 'number'):
                quantity_number = quantity.number
            else:
                quantity_number = Decimal(str(quantity)) if quantity else Decimal('0')
            
            avg_cost_decimal = Decimal(str(avg_cost)) if avg_cost else Decimal('0')
            total_cost_decimal = Decimal(str(total_cost)) if total_cost else Decimal('0')
            
            formatted_quantity = "{:,.2f}".format(quantity_number)
            formatted_avg_cost = "{:,.2f} {}".format(avg_cost_decimal, cost_currency)
            formatted_total_cost = "{:,.2f} {}".format(total_cost_decimal, cost_currency)
            formatted_output.append([str(date), account, formatted_quantity, symbol, formatted_avg_cost, formatted_total_cost])
        else:
            # For detailed lots: date, account, symbol, quantity, cost, cost_currency
            date, account, symbol, quantity, cost, cost_currency = row
            # Extract the number from the Amount object
            if hasattr(quantity, 'number'):
                quantity_number = quantity.number
            else:
                quantity_number = Decimal(str(quantity)) if quantity else Decimal('0')
            
            cost_decimal = Decimal(str(cost)) if cost else Decimal('0')
            
            formatted_quantity = "{:,}".format(int(quantity_number))  # Show as integer since that's how it's displayed in the actual output
            formatted_cost = "{:,.2f} {}".format(cost_decimal, cost_currency)
            formatted_output.append([str(date), account, formatted_quantity, symbol, formatted_cost])

    return formatted_output