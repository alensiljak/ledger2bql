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
from .date_parser import parse_date
from .utils import add_common_arguments, execute_bql_command


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

    add_common_arguments(parser)

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

    return parser


def parse_query(args):
    '''Parse Ledger query into BQL'''
    where_clauses = []
    group_by_clauses = []

    # Handle common arguments
    if args.account_regex:
        for regex in args.account_regex:
            where_clauses.append(f"account ~ '{regex}'")

    if args.begin:
        begin_date = parse_date(args.begin)
        where_clauses.append(f'date >= "{begin_date}"')
    if args.end:
        end_date = parse_date(args.end)
        where_clauses.append(f'date < "{end_date}"')

    # Handle zero balance filtering

    # Handle depth
    if args.depth:
        group_by_clauses.append(f"level(account) <= {args.depth}")

    # Build the final query
    select_clause = "SELECT account, sum(position) as balance"
    query = select_clause

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    return query


def format_output(output: list, args) -> list:
    """Formats the raw output from the BQL query into a pretty-printable list."""
    formatted_output = []
    for row in output:
        if not row:
            continue
        if args.zero and row[-1].is_empty():
            continue
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
            formatted_value = "{:,.2f}".format(amount.units.number)
            
            formatted_balance += f"{formatted_value} {currency_str}"
        
        new_row = list(row)
        new_row[-1] = formatted_balance
        formatted_output.append(tuple(new_row))

    # Handle sorting
    if args.sort:
        # Assuming args.sort can be 'account' or 'balance'
        # For 'account', sort by the first element of the tuple (account name)
        # For 'balance', sort by the numeric value of the balance
        if args.sort == 'account':
            formatted_output.sort(key=lambda x: x[0])
        elif args.sort == 'balance':
            # Need to extract the numeric value from the formatted balance string
            # This is a bit fragile, assuming format is "X.XX CUR"
            formatted_output.sort(key=lambda x: float(x[1].split(' ')[0].replace(',', '')))
    else:
        # Default sort by account
        formatted_output.sort(key=lambda x: x[0])

    return formatted_output


def main():
    """Runs the given query and prints the output in a pretty format."""
    # Determine headers for the table
    headers = ["Account", "Balance"]
    alignments = ["left", "right"]
    
    # Pass args.depth to format_output_func via kwargs
    execute_bql_command(create_parser, parse_query, format_output, headers, alignments)


if __name__ == '__main__':
    main()
