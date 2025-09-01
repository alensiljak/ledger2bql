#!/usr/bin/env python3
# ledger_to_bql_register.py

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
  - `--end DATE` or `-E DATE`   -> `WHERE date < "DATE"`
  - `--total` or `-t`           -> Calculates a running total column
  - `ACCOUNT_REGEX`           -> `WHERE account ~ "ACCOUNT_REGEX"`
"""

import argparse
import os
import sys
from dotenv import load_dotenv
from decimal import Decimal
from collections import defaultdict
from .date_parser import parse_date
# You will need to install the tabulate library for pretty-printing:
# pip install tabulate
from tabulate import tabulate


def create_parser():
    """Define the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Translate ledger-cli register command arguments to a Beanquery (BQL) query.",
        epilog="""
        Note: The `--empty` flag from ledger-cli is generally not needed for BQL
        as `bean-query` typically includes all accounts by default. The `-e` flag is
        supported for consistency but has no effect on the BQL output.
        """
    )
    parser.add_argument(
        'account_regex',
        nargs='*',
        default=None,
        help="Regular expression(s) to filter accounts."
    )
    parser.add_argument(
        '--begin', '-b',
        help="Transactions on or after this date. Format: YYYY-MM-DD."
    )
    parser.add_argument(
        '--end', '-e',
        help="Transactions strictly before this date. Format: YYYY-MM-DD."
    )
    parser.add_argument(
        '--total', '-t',
        action='store_true',
        help="Calculate and display a running total."
    )
    parser.add_argument(
        '--sort', '-S',
        type=str,
        default='date, account',
        help="Sort the results by the given comma-separated fields. Prefix with - for descending order."
    )
    parser.add_argument(
        '--limit',
        type=int,
        help="Limit the number of results."
    )
    return parser


def parse_query():
    """Parse Ledger register command into BQL components."""
    parser = create_parser()
    args = parser.parse_args()

    where_clauses = []
    
    # Handle account regular expressions
    if args.account_regex:
        for regex in args.account_regex:
            where_clauses.append(f"account ~ '{regex}'")

    # Handle date ranges
    if args.begin:
        begin_date = parse_date(args.begin)
        where_clauses.append(f'date >= date("{begin_date}")')
    if args.end:
        end_date = parse_date(args.end)
        where_clauses.append(f'date < date("{end_date}")')

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
    
    print(f"\nYour BQL query is:\n\n{query}\n")

    return query, args


def run_bql_query(query: str, book: str) -> list:
    """Run the BQL query and return results."""
    import beanquery

    # Create the connection.
    connection = beanquery.connect("beancount:" + book)

    # Run the query
    cursor = connection.execute(query)
    result = cursor.fetchall()

    return result


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
        formatted_transaction_amount = f"{transaction_amount:,f} {transaction_currency}"
        
        # Format the running total
        formatted_running_total = f"{running_total[transaction_currency]:,f} {transaction_currency}"
        
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
    load_dotenv()
    BEANCOUNT_FILE = os.getenv("BEANCOUNT_FILE")
    if not BEANCOUNT_FILE:
        raise Exception('Beancount file not set.')

    query, args = parse_query()
    output = run_bql_query(query, BEANCOUNT_FILE)
    
    formatted_output = format_output(output, args.total)

    if args.limit:
        formatted_output = formatted_output[:args.limit]

    # Determine headers and alignments for the table
    headers = ["Date", "Account", "Payee", "Narration", "Amount"]
    alignments = ["left", "left", "left", "left", "right"]

    if args.total:
        headers.append("Running Total")
        alignments.append("right")

    # Pretty-print the results
    print("Query Results:")
    print(tabulate(formatted_output, headers=headers, tablefmt="psql", colalign=alignments))


if __name__ == '__main__':
    main()
