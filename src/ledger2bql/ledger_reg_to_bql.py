"""
A command-line tool to translate ledger-cli 'register' command syntax
into a Beanquery (BQL) query.

Usage:
  python ledger_to_bql_register.py [options] [ACCOUNT_REGEX]

Example:
  # Translate a ledger command to show a register for all accounts.
  # This command is equivalent to `ledger reg`
  python ledger_to_bql_register.py

  # Translate a command for a specific account with a running total.
  # This is equivalent to `ledger reg Expenses --total`
  python ledger_to_bql_register.py Expenses --total

  # Translate a command with a date range and multiple account filters.
  # This is equivalent to `ledger reg income expenses --begin 2024-01-01 --end 2024-02-01`
  python ledger_to_bql_register.py income expenses -b 2024-01-01 -E 2024-02-01

Key Mappings:
  - `--begin DATE` or `-b DATE` -> `WHERE date >= "DATE"`
  - `--end DATE` or `-e DATE`   -> `WHERE date < "DATE"`
  - `--total` or `-t`           -> Calculates a running total column
  - `ACCOUNT_REGEX`           -> `WHERE account ~ "ACCOUNT_REGEX"`
  - `@DESCRIPTION_REGEX   -> `WHERE description ~ "DESCRIPTION_REGEX"`
"""

import argparse
from decimal import Decimal
from collections import defaultdict
from .date_parser import parse_date
from .utils import add_common_arguments, execute_bql_command, parse_amount_filter


def create_parser():
    """Define the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Translate ledger-cli register command arguments to a Beanquery (BQL) query.",
        epilog="""
        Note: The `--empty` flag from ledger-cli is generally not needed for BQL
        as `bean-query` typically includes all accounts by default.
        """
    )
    add_common_arguments(parser)
    # Override the default sort for 'reg' to be no sort
    parser.set_defaults(sort=None)
    parser.add_argument(
        '--total', '-t',
        action='store_true',
        help="Calculate and display a running total.",
        default=False
    )
    return parser


def parse_query(args):
    where_clauses = []
    account_regexes = []
    
    # Handle account regular expressions and payee filters
    if args.account_regex:
        for regex in args.account_regex:
            if regex.startswith('@'):
                payee = regex[1:]
                where_clauses.append(f"description ~ '{payee}'")
            else:
                account_regexes.append(regex)

    if account_regexes:
        for regex in account_regexes:
            where_clauses.append(f"account ~ '{regex}'")

    # Handle date ranges
    if args.begin:
        begin_date = parse_date(args.begin)
        where_clauses.append(f'date >= date("{begin_date}")')
    if args.end:
        end_date = parse_date(args.end)
        where_clauses.append(f'date < date("{end_date}")')

    # Handle amount filters
    if args.amount:
        for amount_filter in args.amount:
            op, val, cur = parse_amount_filter(amount_filter)
            amount_clause = f"number {op} {val}"
            if cur:
                amount_clause += f" AND currency = '{cur}'"
            where_clauses.append(amount_clause)

    # Build the final query
    select_clause = "SELECT date, account, payee, narration, position"
    query = select_clause

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    # Handle sorting
    if args.sort:
        sort_keys = []
        for key in args.sort.split(','):
            key = key.strip()
            if key.startswith('-'):
                sort_keys.append(f"{key[1:]} DESC")
            else:
                sort_keys.append(key)
        query += " ORDER BY " + ", ".join(sort_keys)

    return query


def format_output(output: list, show_total: bool) -> list:
    """Formats the raw output from the BQL query into a pretty-printable list."""
    formatted_output = []
    running_total = defaultdict(Decimal)

    for row in output:
        date, account, payee, narration, position = row
        
        # Access the amount from the position object
        transaction_amount = position.units.number.normalize()
        transaction_currency = position.units.currency
        
        # Calculate running total
        running_total[transaction_currency] += transaction_amount

        # Format the transaction amount
        formatted_transaction_amount = "{:,.2f} {}".format(transaction_amount, transaction_currency)
        
        # Format the running total
        formatted_running_total = "{:,.2f} {}".format(running_total[transaction_currency], transaction_currency)
        
        # Assemble the row
        new_row = [
            date,
            account,
            payee,
            narration,
            formatted_transaction_amount
        ]

        if show_total:
            new_row.append(formatted_running_total)
        
        formatted_output.append(new_row)

    return formatted_output


def main():
    """Runs the given query and prints the output in a pretty format."""
    def format_output_with_args(output, args):
        formatted = format_output(output, args.total)
        if args.limit:
            formatted = formatted[:args.limit]
        return formatted

    # Determine headers and alignments for the table
    headers = ["Date", "Account", "Payee", "Narration", "Amount"]
    alignments = ["left", "left", "left", "left", "right"]

    execute_bql_command(create_parser, parse_query, format_output_with_args, 
                        headers, alignments)


if __name__ == '__main__':
    main()