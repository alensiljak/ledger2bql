"""
A command-line tool to translate ledger-cli 'assert' command syntax
into a Beanquery (BQL) query.
"""

import click
from .date_parser import parse_date, parse_date_range
from .utils import (
    add_common_click_arguments,
    execute_bql_command_with_click,
    parse_account_params,
    parse_account_pattern,
    parse_amount_filter,
)


@click.command(name="assert", short_help="[a] Show balance assertions")
@click.argument("account_regex", nargs=-1)
@add_common_click_arguments
def assert_command(account_regex, **kwargs):
    """Translate ledger-cli assert command arguments to a Beanquery (BQL) query."""

    # Package arguments in a way compatible with the existing code
    class Args:
        def __init__(self, account_regex, **kwargs):
            self.account_regex = account_regex
            for key, value in kwargs.items():
                setattr(self, key, value)

    args = Args(account_regex, **kwargs)

    # Determine headers for the table
    headers = ["Date", "Account", "Balance"]
    alignments = ["left", "left", "right"]

    # Execute the command
    execute_bql_command_with_click(
        parse_query, format_output, headers, alignments, args, command_type="assert"
    )


def parse_query(args):
    """Parse Ledger query into BQL"""
    where_clauses = []

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
            amount_clause = f"amount.number {op} {val}"
            if cur:
                amount_clause += f" AND amount.currency = '{cur}'"
            where_clauses.append(amount_clause)

    # Handle currency filter
    if hasattr(args, "currency") and args.currency:
        if isinstance(args.currency, list):
            currencies_str = "', '".join(args.currency)
            where_clauses.append(f"amount.currency IN ('{currencies_str}')")
        else:
            where_clauses.append(f"amount.currency = '{args.currency}'")

    # Build the final query for #balances table
    # The #balances table has columns: date, account, amount, None, calculated_amount
    # We want to select date, account, and the amount (balance)
    if hasattr(args, "exchange") and args.exchange:
        # When exchange currency is specified, we need to handle conversion differently
        # For now, let's just select the basic columns and handle conversion in formatting
        select_clause = "SELECT date, account, amount"
    else:
        select_clause = "SELECT date, account, amount"
    query = select_clause

    query += " FROM #balances"

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

            if field == "balance":
                sort_fields.append(f"sum(position) {sort_order}")
            else:
                sort_fields.append(f"{field} {sort_order}")
        query += " ORDER BY " + ", ".join(sort_fields)

    # Handle limit
    if hasattr(args, "limit") and args.limit:
        query += f" LIMIT {args.limit}"

    return query


def format_output(output: list, args) -> list:
    """Formats the raw output from the BQL query into a pretty-printable list."""
    formatted_output = []

    for row in output:
        if not row:
            continue

        date = row[0]
        account_name = row[1]
        amount_obj = row[2]  # This is a beancount.core.amount.Amount object

        # Format the amount object
        # The Amount object has a number and currency attribute
        formatted_balance = "{:,.2f} {}".format(amount_obj.number, amount_obj.currency)

        # Assemble the row
        new_row = [date, account_name, formatted_balance]
        formatted_output.append(tuple(new_row))

    return formatted_output
