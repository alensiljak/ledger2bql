import argparse
import os
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
        '--end', '-E',
        help='End date for the query (YYYY-MM-DD).'
    )
    parser.add_argument(
        '--empty', '-e',
        action='store_true',
        help='Show accounts with zero balance (for consistency with ledger-cli, no effect on BQL).'
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

def execute_bql_command(create_parser_func, parse_query_func, format_output_func, headers, alignments, **kwargs):
    """
    Executes a BQL command by parsing arguments, constructing a query, running it, and formatting output.
    """
    parser = create_parser_func()
    args = parser.parse_args()

    book = get_beancount_file_path()

    query = parse_query_func(args)

    output = run_bql_query(query, book)

    # Pass kwargs to format_output_func
    formatted_output = format_output_func(output, args)

    if not formatted_output: # Handle empty output
        print("No records found.")
        return

    # Print the BQL query
    print(f"\nYour BQL query is:\n\n{query}\n")

    # Determine headers and alignments for the table based on args
    if hasattr(args, 'total') and args.total:
        headers.append("Running Total")
        alignments.append("right")

    print(tabulate(formatted_output, headers=headers, tablefmt="psql", colalign=alignments))
