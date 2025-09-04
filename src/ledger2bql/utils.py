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
import click


def get_beancount_file_path():
    """Get the path to the beancount file from environment variable."""
    beancount_file = os.getenv('BEANCOUNT_FILE')
    if not beancount_file:
        raise ValueError("BEANCOUNT_FILE environment variable not set.")
    return beancount_file


def parse_account_pattern(pattern):
    """
    Parse account pattern and convert to appropriate regex pattern for BQL.
    
    Supports:
    - ^pattern (starts with)
    - pattern$ (ends with)
    - ^pattern$ (exact match)
    - pattern (regex match, default)
    
    Returns a formatted regex pattern string.
    """
    import re
    if pattern.startswith('^') and pattern.endswith('$'):
        # Exact match: ^pattern$
        exact_match = pattern[1:-1]  # Remove both ^ and $
        # Create a regex that matches the exact string
        regex_pattern = f'^{re.escape(exact_match)}$'
        return regex_pattern
    elif pattern.startswith('^'):
        # Starts with: ^pattern
        starts_with = pattern[1:]  # Remove ^
        # Create a regex that matches strings starting with this pattern
        regex_pattern = f'^{re.escape(starts_with)}'
        return regex_pattern
    elif pattern.endswith('$'):
        # Ends with: pattern$
        ends_with = pattern[:-1]  # Remove $
        # Create a regex that matches strings ending with this pattern
        regex_pattern = f'{re.escape(ends_with)}$'
        return regex_pattern
    else:
        # Regex match (default behavior)
        return pattern


def add_common_arguments(parser):
    """Add common arguments to an argparse parser."""
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
        help='Date range in format YYYY..YYYY, YYYY-MM..YYYY-MM, or YYYY-MM-DD..YYYY-MM-DD. Shorthand syntax: YYYY, YYYY-MM, YYYY-MM-DD, YYYY.., ..YYYY, etc.'
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
        '--exchange', '-X',
        type=str.upper,
        help='Convert all amounts to the specified currency.'
    )
    parser.add_argument(
        '--total', '-T',
        action='store_true',
        help='Show a grand total row at the end of the balance report or a running total column in the register report.'
    )
    parser.add_argument(
        '--no-pager',
        action='store_true',
        help='Disable automatic paging of output.'
    )


def add_common_click_arguments(func):
    """Decorator to add common arguments to a Click command."""
    # Define the common options
    func = click.option('--begin', '-b', help='Start date for the query (YYYY-MM-DD).')(func)
    func = click.option('--end', '-e', help='End date for the query (YYYY-MM-DD).')(func)
    func = click.option('--date-range', '-d', help='Date range in format YYYY..YYYY, YYYY-MM..YYYY-MM, or YYYY-MM-DD..YYYY-MM-DD. Shorthand syntax: YYYY, YYYY-MM, YYYY-MM-DD, YYYY.., ..YYYY, etc.')(func)
    func = click.option('--empty', is_flag=True, help='Show accounts with zero balance (for consistency with ledger-cli, no effect on BQL).')(func)
    func = click.option('--sort', '-S', default='account', help='Sort the results by the given comma-separated fields. Prefix with - for descending order.')(func)
    func = click.option('--limit', type=int, help='Limit the number of results.')(func)
    func = click.option('--amount', '-a', multiple=True, help='Filter by amount. Format: [>|>=|<|<=|=]AMOUNT[CURRENCY]. E.g. >100EUR')(func)
    func = click.option('--currency', '-c', help='Filter by currency. E.g. EUR or EUR,BAM')(func)
    func = click.option('--exchange', '-X', type=str.upper, help='Convert all amounts to the specified currency.')(func)
    func = click.option('--total', '-T', is_flag=True, help='Show a grand total row at the end of the balance report or a running total column in the register report.')(func)
    func = click.option('--no-pager', is_flag=True, help='Disable automatic paging of output.')(func)
    return func


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
    
    # For commands with --exchange, add a Converted column
    if hasattr(args, 'exchange') and args.exchange:
        if command_type == 'bal':
            headers.append(f"Total ({args.exchange})")
            alignments.append("right")
        elif command_type == 'reg':
            headers.append(f"Amount ({args.exchange})")
            alignments.append("right")
            # If total is also requested, add a converted total column
            if hasattr(args, 'total') and args.total:
                headers.append(f"Total ({args.exchange})")
                alignments.append("right")

    # Generate the table output
    table_output = tabulate(formatted_output, headers=headers, tablefmt="psql", 
                            colalign=alignments)
    
    # Use pager unless explicitly disabled with --no-pager
    use_pager = not getattr(args, 'no_pager', False)
    
    if use_pager:
        click.echo_via_pager(table_output)
    else:
        print(table_output)


def execute_bql_command_with_click(parse_query_func, format_output_func,
                                   headers, alignments, args, command_type=None):
    """
    Executes a BQL command with Click arguments, constructing a query, running it,
    and formatting output.
    """
    # Process the currency argument
    if hasattr(args, 'currency') and args.currency:
        # Split comma-separated currencies and convert to uppercase
        if ',' in args.currency:
            args.currency = [currency.upper() for currency in args.currency.split(',')]
        else:
            args.currency = args.currency.upper()
    
    # Convert amount from tuple (Click's multiple) to list (as expected by existing code)
    if hasattr(args, 'amount') and args.amount:
        args.amount = list(args.amount)

    book = get_beancount_file_path()

    query = parse_query_func(args)
    output = run_bql_query(query, book)

    # Pass kwargs to format_output_func
    formatted_output = format_output_func(output, args)

    if not formatted_output: # Handle empty output
        click.echo("No records found.")
        return

    # Print the BQL query
    click.echo(f"\nYour BQL query is:\n{query}\n")

    # Determine headers and alignments for the table based on args
    # For register command with --total, add a Running Total column
    if hasattr(args, 'total') and args.total and command_type == 'reg':
        headers.append("Running Total")
        alignments.append("right")
    
    # For commands with --exchange, add a Converted column
    if hasattr(args, 'exchange') and args.exchange:
        if command_type == 'bal':
            headers.append(f"Total ({args.exchange})")
            alignments.append("right")
        elif command_type == 'reg':
            headers.append(f"Amount ({args.exchange})")
            alignments.append("right")
            # If total is also requested, add a converted total column
            if hasattr(args, 'total') and args.total:
                headers.append(f"Total ({args.exchange})")
                alignments.append("right")

    # Generate the table output
    table_output = tabulate(formatted_output, headers=headers, tablefmt="psql", 
                            colalign=alignments)
    
    # Use pager unless explicitly disabled with --no-pager
    use_pager = not getattr(args, 'no_pager', False)
    
    if use_pager:
        click.echo_via_pager(table_output)
    else:
        click.echo(table_output)