'''
Shared utilities.
'''
import argparse
import os
import re
import sys
from decimal import Decimal
import beanquery
from tabulate import tabulate


def get_beancount_file_path():
    """Placeholder for get_beancount_file_path."""
    # This function should ideally get the path to the beancount file, e.g., from an environment variable.
    # For now, returning a placeholder or raising an error.
    beancount_file = os.getenv('BEANCOUNT_FILE')
    if not beancount_file:
        raise ValueError("BEANCOUNT_FILE environment variable not set.")
    return beancount_file


def add_common_arguments(parser):
    """Placeholder for add_common_arguments."""
    parser.add_argument(
        'account_regex',
        nargs='*',
        help='Regular expression to match account names.'
    )
    parser.add_argument(
        '--begin', '-b',
        help='Start date for the query (YYYY-MM-DD).'
    )
    parser.add_argument(
        '--end', '-e',
        help='End date for the query (YYYY-MM-DD).'
    )
    parser.add_argument(
        '--date-range', '-d',
        help='Date range in format YYYY..YYYY, YYYY-MM..YYYY-MM, or YYYY-MM-DD..YYYY-MM-DD'
    )
    parser.add_argument(
        '--empty',
        # '-e',
        action='store_true',
        help='Show accounts with zero balance (for consistency with ledger-cli, no effect on BQL).'
    )
    parser.add_argument(
        '--sort', '-S',
        type=str,
        default='account',
        help="Sort the results by the given comma-separated fields. Prefix with - for descending order."
    )
    parser.add_argument(
        '--limit',
        type=int,
        help="Limit the number of results."
    )
    parser.add_argument(
        '--amount', '-a',
        action='append',
        help='Filter by amount. Format: [>|>=|<|<=|=]AMOUNT[CURRENCY]. E.g. >100EUR'
    )
    parser.add_argument(
        '--currency', '-c',
        type=lambda x: [currency.upper() for currency in x.split(',')] if x and ',' in x else (x.upper() if x else None),
        help='Filter by currency. E.g. EUR or EUR,BAM'
    )
    parser.add_argument(
        '--total', '-T',
        action='store_true',
        help='Show a grand total row at the end of the balance report or a running total column in the register report.'
    )


def run_bql_query(query: str, book: str) -> list:
    """
    Run the BQL query and return results
    book: Path to beancount file.
    """
    # Create the connection. Pre-load the beanquery data.
    connection = beanquery.connect("beancount:" + book)

    # Run the query
    cursor = connection.execute(query)
    result = cursor.fetchall()

    return result


def parse_amount_filter(amount_str):
    """
    Parses an amount filter string into a (operator, value, currency) tuple.
    """
    match = re.match(r'([><]=?|=)?(-?\d+\.?\d*)([A-Z]{3})?', amount_str, re.IGNORECASE)
    if not match:
        raise ValueError(f"Invalid amount filter format: {amount_str}")
    
    op, val_str, cur = match.groups()
    
    op = op or '='
    val = Decimal(val_str)
    
    if cur:
        cur = cur.upper()
    
    return op, val, cur


def execute_bql_command(create_parser_func, parse_query_func, format_output_func, 
                        headers, alignments, command_type=None, **kwargs):
    """
    Executes a BQL command by parsing arguments, constructing a query, running it, 
    and formatting output.
    """
    parser = create_parser_func()
    args, remaining_args = parser.parse_known_args()
    if remaining_args:
        if not args.account_regex:
            args.account_regex = []
        args.account_regex.extend(remaining_args)

    book = get_beancount_file_path()

    query = parse_query_func(args)
    output = run_bql_query(query, book)

    # Pass kwargs to format_output_func
    formatted_output = format_output_func(output, args)

    if not formatted_output: # Handle empty output
        print("No records found.")
        return

    # Print the BQL query
    print(f"\nYour BQL query is:\n{query}\n")

    # Determine headers and alignments for the table based on args
    # For register command with --total, add a Running Total column
    if hasattr(args, 'total') and args.total and command_type == 'reg':
        headers.append("Running Total")
        alignments.append("right")

    print(tabulate(formatted_output, headers=headers, tablefmt="psql", 
                   colalign=alignments))
