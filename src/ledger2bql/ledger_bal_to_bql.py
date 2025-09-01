#!/usr/bin/env python3
# ledger_to_bql.py

"""
A command-line tool to translate ledger-cli 'balance' command syntax
into a Beanquery (BQL) query.

Usage:
  python ledger_to_bql.py [options] [ACCOUNT_REGEX]

Example:
  # Translate a ledger command to show balances with a depth of 2, excluding zero-balance accounts.
  # This command is equivalent to `ledger bal -d 2 -Z`
  python ledger_to_bql.py -d 2 -Z

  # Translate a command for a specific account with a date range.
  # This is equivalent to `ledger bal Expenses --begin 2024-01-01 --end 2024-02-01`
  python ledger_to_bql.py Expenses -b 2024-01-01 -E 2024-02-01

  # Translate a command with multiple account filters.
  # This is equivalent to `ledger bal income expenses`
  python ledger_to_bql.py income expenses

Key Mappings:
  - `--depth X` or `-d X` -> `GROUP BY level(account) <= X`
  - `--zero` or `-Z`       -> `WHERE balance != 0` (removes accounts with zero balance)
  - `--begin DATE` or `-b DATE` -> `WHERE date >= "DATE"`
  - `--end DATE` or `-E DATE`   -> `WHERE date < "DATE"`
  - `ACCOUNT_REGEX`           -> `WHERE account ~ "ACCOUNT_REGEX"`
"""

import argparse
import os
import sys
from dotenv import load_dotenv
from decimal import Decimal
from .date_parser import parse_date
# You will need to install the tabulate library for pretty-printing:
# pip install tabulate
from tabulate import tabulate


def create_parser():
    '''Define the query parser'''
    parser = argparse.ArgumentParser(
        description="Translate ledger-cli balance command arguments to a Beanquery (BQL) query.",
        epilog="""
        Note: The `--empty` flag from ledger-cli is generally not needed for BQL
        as `bean-query` typically includes all accounts by default. The `-e` flag is
        supported for consistency but has no effect on the BQL output.
        """
    )

    parser.add_argument(
        'account_regex',
        nargs='*', # Changed to accept multiple arguments
        default=None,
        help="Regular expression(s) to filter accounts."
    )
    parser.add_argument(
        '--depth', '-d',
        type=int,
        help="Show accounts up to a certain depth (level) in the account tree."
    )
    parser.add_argument(
        '--zero', '-Z',
        action='store_true',
        help="Exclude accounts with a zero balance."
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
        '--limit',
        type=int,
        help="Limit the number of results."
    )

    return parser


def parse_query():
    '''Parse Ledger query into BQL'''
    parser = create_parser()
    args = parser.parse_args()

    where_clauses = []
    group_by_clauses = []

    # 1. Handle account regular expression (now supports multiple)
    if args.account_regex:
        for regex in args.account_regex:
            where_clauses.append(f"account ~ '{regex}'")

    # 2. Handle date ranges
    if args.begin:
        begin_date = parse_date(args.begin)
        where_clauses.append(f'date >= "{begin_date}"')
    if args.end:
        end_date = parse_date(args.end)
        where_clauses.append(f'date < "{end_date}"')

    # 3. Handle zero balance filtering
    if args.zero:
        where_clauses.append("balance != 0")

    # 4. Handle depth
    if args.depth:
        group_by_clauses.append(f"level(account) <= {args.depth}")

    # Build the final query
    select_clause = "SELECT account, sum(position) as balance"
    if group_by_clauses:
        select_clause = "SELECT account, level(account), balance"

    query = select_clause

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    if group_by_clauses:
        query += " GROUP BY " + ", ".join(group_by_clauses)

    print(f"\nYour BQL query is:\n\n{query}\n")

    return query, args


def run_bql_query(query: str, book: str) -> list:
    '''Run the BQL query and return results
    book: Path to beancount file.
    '''
    import beanquery

    # Create the connection. Pre-load the beanquery data.
    connection = beanquery.connect("beancount:" + book)

    # Run the query
    cursor = connection.execute(query)
    result = cursor.fetchall()

    return result


def format_output(output: list) -> list:
    """Formats the raw output from the BQL query into a pretty-printable list."""
    formatted_output = []
    for row in output:
        # The balance is always the last element in the row tuple
        balance_inventory = row[-1]
        
        # An Inventory object can contain multiple currencies. We need to iterate
        # through its items, which are (currency, Position) pairs.
        formatted_balance = ""
        for currency, amount in balance_inventory.items():
            # Check if the currency is a tuple and extract the string
            if isinstance(currency, tuple):
                currency_str = currency[0]
            else:
                currency_str = currency

            # Correctly access the number from the Position object's `units`
            formatted_value = f"{amount.units.number.normalize():,f}"
            
            formatted_balance += f"{formatted_value} {currency_str}"
        
        new_row = list(row)
        new_row[-1] = formatted_balance
        formatted_output.append(tuple(new_row))
    return formatted_output


def main():
    """Runs the given query and prints the output in a pretty format."""
    # Get environment variables
    load_dotenv()
    BEANCOUNT_FILE = os.getenv("BEANCOUNT_FILE")
    if not BEANCOUNT_FILE:
        raise Exception('Beancount file not set.')

    query, args = parse_query()
    output = run_bql_query(query, BEANCOUNT_FILE)
    
    # Format the output to remove the parentheses
    formatted_output = format_output(output)

    if args.limit:
        formatted_output = formatted_output[:args.limit]

    # Determine headers for the table
    headers = ["Account", "Balance"]
    alignments = ["left", "right"]
    if args.depth:
        headers = ["Account", "Level", "Balance"]
        alignments = ["left", "left", "right"]

    # Pretty-print the results
    print("Query Results:")
    print(tabulate(formatted_output, headers=headers, tablefmt="psql", colalign=alignments))


if __name__ == '__main__':
    main()
