"""
A command-line tool to translate ledger-cli 'register' command syntax
into a Beanquery (BQL) query.
"""

import click
from decimal import Decimal
from collections import defaultdict
from .date_parser import parse_date, parse_date_range
from .utils import add_common_click_arguments, execute_bql_command_with_click, parse_amount_filter, parse_account_pattern


@click.command(name='reg', short_help='Show transaction register')
@click.argument('account_regex', nargs=-1)
@add_common_click_arguments
@click.pass_context
def reg_command(ctx, account_regex, **kwargs):
    """Translate ledger-cli register command arguments to a Beanquery (BQL) query."""
    # Package arguments in a way compatible with the existing code
    class Args:
        def __init__(self, account_regex, **kwargs):
            self.account_regex = account_regex
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    args = Args(account_regex, **kwargs)
    
    # Determine headers and alignments for the table
    headers = ["Date", "Account", "Payee", "Narration", "Amount"]
    alignments = ["left", "left", "left", "left", "right"]
    
    # Execute the command
    execute_bql_command_with_click(parse_query, format_output, headers, alignments, args, command_type='reg')


def parse_query(args):
    where_clauses = []
    account_regexes = []
    excluded_account_regexes = []
    
    # Handle account regular expressions and payee filters
    if args.account_regex:
        i = 0
        while i < len(args.account_regex):
            regex = args.account_regex[i]
            if regex == 'not':
                # The next argument(s) should be excluded
                i += 1
                while i < len(args.account_regex):
                    next_regex = args.account_regex[i]
                    if next_regex.startswith('@') or next_regex == 'not':
                        # If we encounter another @ pattern or 'not', stop excluding
                        i -= 1  # Step back to process this in the next iteration
                        break
                    else:
                        excluded_account_regexes.append(next_regex)
                        i += 1
            elif regex.startswith('@'):
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
    if hasattr(args, 'begin') and args.begin:
        begin_date = parse_date(args.begin)
        where_clauses.append(f'date >= date("{begin_date}")')
    if hasattr(args, 'end') and args.end:
        end_date = parse_date(args.end)
        where_clauses.append(f'date < date("{end_date}")')
    
    # Handle date range if provided
    if hasattr(args, 'date_range') and args.date_range:
        begin_date, end_date = parse_date_range(args.date_range)
        if begin_date:
            where_clauses.append(f'date >= date("{begin_date}")')
        if end_date:
            where_clauses.append(f'date < date("{end_date}")')

    # Handle amount filters
    if hasattr(args, 'amount') and args.amount:
        for amount_filter in args.amount:
            op, val, cur = parse_amount_filter(amount_filter)
            amount_clause = f"number {op} {val}"
            if cur:
                amount_clause += f" AND currency = '{cur}'"
            where_clauses.append(amount_clause)
    
    # Handle currency filter
    if hasattr(args, 'currency') and args.currency:
        if isinstance(args.currency, list):
            currencies_str = "', '".join(args.currency)
            where_clauses.append(f"currency IN ('{currencies_str}')")
        else:
            where_clauses.append(f"currency = '{args.currency}'")

    # Build the final query
    if hasattr(args, 'exchange') and args.exchange:
        # When exchange currency is specified, convert positions to that currency
        select_clause = f"SELECT date, account, payee, narration, position, convert(position, '{args.exchange}') as converted_position"
    else:
        select_clause = "SELECT date, account, payee, narration, position"
    query = select_clause

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    # Handle sorting
    # Ignore default sorting by 'account' for register command
    if hasattr(args, 'sort') and args.sort and args.sort != 'account':
        sort_keys = []
        for key in args.sort.split(','):
            key = key.strip()
            if key.startswith('-'):
                sort_keys.append(f"{key[1:]} DESC")
            else:
                sort_keys.append(key)
        query += " ORDER BY " + ", ".join(sort_keys)

    return query


def format_output(output: list, args) -> list:
    """Formats the raw output from the BQL query into a pretty-printable list."""
    formatted_output = []
    running_total = defaultdict(Decimal)
    converted_running_total = Decimal('0')

    for row in output:
        if args.exchange:
            # When exchange currency is specified, we have an additional column with converted position
            date, account, payee, narration, position, converted_position = row
            
            # Access the amount from the position object
            transaction_amount = position.units.number.normalize()
            transaction_currency = position.units.currency
            
            # Calculate running total
            running_total[transaction_currency] += transaction_amount

            # Format the transaction amount
            formatted_transaction_amount = "{:,.2f} {}".format(transaction_amount, transaction_currency)
            
            # Format the converted amount
            converted_amount = converted_position
            formatted_converted_amount = "{:,.2f} {}".format(converted_amount.number, converted_amount.currency)
            
            # Calculate converted running total
            # Only add to the converted running total if the conversion was successful
            if converted_amount.currency == args.exchange:
                converted_running_total += converted_amount.number
            
            # Format the running totals
            formatted_running_total = "{:,.2f} {}".format(running_total[transaction_currency], transaction_currency)
            formatted_converted_running_total = "{:,.2f} {}".format(converted_running_total, args.exchange)
            
            # Assemble the row
            new_row = [
                date,
                account,
                payee,
                narration,
                formatted_transaction_amount
            ]
            
            # Add running total if total is requested
            if args.total:
                new_row.append(formatted_running_total)
                
            # Add converted amount if exchange is requested
            if args.exchange:
                new_row.append(formatted_converted_amount)
                
            # Add converted running total if both exchange and total are requested
            if args.exchange and args.total:
                new_row.append(formatted_converted_running_total)
        else:
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
            
            # Add running total if total is requested
            if args.total:
                new_row.append(formatted_running_total)
        
        formatted_output.append(new_row)

    return formatted_output


