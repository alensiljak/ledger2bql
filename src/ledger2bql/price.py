"""
A command-line tool to translate ledger-cli 'price' command syntax
into a Beanquery (BQL) query.
"""

import click
from .date_parser import parse_date, parse_date_range
from .utils import (
    add_common_click_arguments,
    execute_bql_command_with_click,
    parse_amount_filter,
)


@click.command(name="price", short_help="[p] Show price history")
@click.argument("symbol_filter", nargs=-1, required=False)
@add_common_click_arguments
def price_command(symbol_filter, **kwargs):
    """Translate ledger-cli price command arguments to a Beanquery (BQL) query.
    
    Examples:
        ledger2bql price                    # Show all prices
        ledger2bql price ABC               # Show prices for symbol ABC
        ledger2bql price --begin 2025-01-01 # Show prices from 2025 onwards
        ledger2bql price --currency EUR    # Show prices in EUR
        ledger2bql price -a ">1.2"          # Show prices greater than 1.2 (use quotes!)
        ledger2bql price -a ">1.2EUR"       # Show EUR prices greater than 1.2
    """
    
    # Package arguments in a way compatible with the existing code
    class Args:
        def __init__(self, symbol_filter, **kwargs):
            self.symbol_filter = symbol_filter
            for key, value in kwargs.items():
                setattr(self, key, value)

    args = Args(symbol_filter, **kwargs)

    # Determine headers for the table
    headers = ["Date", "Symbol", "Price"]
    alignments = ["left", "left", "right"]

    # Execute the command
    execute_bql_command_with_click(
        parse_query, format_output, headers, alignments, args, command_type="price"
    )


def parse_query(args):
    """Parse Ledger query into BQL"""
    where_clauses = []

    # Handle symbol filters
    if hasattr(args, "symbol_filter") and args.symbol_filter:
        symbol_patterns = []
        for symbol in args.symbol_filter:
            # For now, use simple regex matching for symbols
            # Could be enhanced with pattern matching like accounts
            symbol_patterns.append(f"currency ~ '{symbol}'")
        
        if symbol_patterns:
            where_clauses.append("(" + " OR ".join(symbol_patterns) + ")")

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

    # Handle amount filters - for prices, we need to filter on the amount column
    if hasattr(args, "amount") and args.amount:
        for amount_filter in args.amount:
            op, val, cur = parse_amount_filter(amount_filter)
            # For prices table, we filter on the amount's number property
            amount_clause = f"amount.number {op} {val}"
            if cur:
                amount_clause += f" AND amount.currency = '{cur}'"
            where_clauses.append(amount_clause)

    # Handle currency filter
    if hasattr(args, "currency") and args.currency:
        if isinstance(args.currency, list):
            currencies_str = "', '".join(args.currency)
            where_clauses.append(f"currency IN ('{currencies_str}')")
        else:
            where_clauses.append(f"currency = '{args.currency}'")

    # Build the final query
    select_clause = "SELECT date, currency, amount FROM #prices"
    query = select_clause

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    # Handle sorting
    if hasattr(args, "sort") and args.sort:
        sort_fields = []
        for field in args.sort.split(","):
            field = field.strip()
            sort_order = "ASC"
            if field.startswith("-"):
                field = field[1:]
                sort_order = "DESC"

            # Map friendly field names to actual column names
            field_mapping = {
                "date": "date",
                "symbol": "currency",
                "price": "amount",
                "amount": "amount"
            }
            actual_field = field_mapping.get(field, field)
            sort_fields.append(f"{actual_field} {sort_order}")
        query += " ORDER BY " + ", ".join(sort_fields)

    # Handle limit
    if hasattr(args, "limit") and args.limit:
        query += f" LIMIT {args.limit}"

    return query


def format_output(output: list, args) -> list:
    """Formats the raw output from the BQL query into a pretty-printable list."""
    formatted_output = []

    for row in output:
        if not row or len(row) < 3:
            continue

        date, symbol, amount_obj = row

        # Format the amount
        if hasattr(amount_obj, 'number') and hasattr(amount_obj, 'currency'):
            formatted_amount = "{:,.6f} {}".format(amount_obj.number, amount_obj.currency)
        else:
            formatted_amount = str(amount_obj)

        # Format the date
        formatted_date = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)

        formatted_output.append([formatted_date, symbol, formatted_amount])

    return formatted_output


# Import the parse_amount_filter function from utils
from .utils import parse_amount_filter