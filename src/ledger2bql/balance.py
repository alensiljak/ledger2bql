"""
A command-line tool to translate ledger-cli 'balance' command syntax
into a Beanquery (BQL) query.
"""

import click
from .date_parser import parse_date, parse_date_range
from .utils import add_common_click_arguments, execute_bql_command_with_click, parse_amount_filter


@click.command(name='bal', short_help='Show account balances')
@click.option('--depth', '-D', type=int, help='Show accounts up to a certain depth (level) in the account tree.')
@click.option('--zero', '-Z', is_flag=True, help='Exclude accounts with a zero balance.')
@click.argument('account_regex', nargs=-1)
@add_common_click_arguments
def bal_command(account_regex, depth, zero, **kwargs):
    """Translate ledger-cli balance command arguments to a Beanquery (BQL) query."""
    # Package arguments in a way compatible with the existing code
    class Args:
        def __init__(self, account_regex, depth, zero, **kwargs):
            self.account_regex = account_regex
            self.depth = depth
            self.zero = zero
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    args = Args(account_regex, depth, zero, **kwargs)
    
    # Determine headers for the table
    headers = ["Account", "Balance"]
    alignments = ["left", "right"]
    
    # Execute the command
    execute_bql_command_with_click(parse_query, format_output, headers, alignments, args, command_type='bal')


def parse_query(args):
    '''Parse Ledger query into BQL'''
    where_clauses = []
    group_by_clauses = []
    account_regexes = []
    excluded_account_regexes = []

    # Handle common arguments
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
        for regex in account_regexes:
            where_clauses.append(f"account ~ '{regex}'")
    
    if excluded_account_regexes:
        for regex in excluded_account_regexes:
            where_clauses.append(f"NOT (account ~ '{regex}')")

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
        # When exchange currency is specified, convert all positions to that currency
        select_clause = f"SELECT account, units(sum(position)) as Balance, convert(sum(position), '{args.exchange}') as Converted"
    else:
        select_clause = "SELECT account, units(sum(position)) as Balance"
    query = select_clause

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    if group_by_clauses:
        query += " GROUP BY " + ", ".join(group_by_clauses)

    if hasattr(args, 'sort') and args.sort:
        sort_fields = []
        for field in args.sort.split(','):
            field = field.strip()
            sort_order = "ASC"
            if field.startswith('-'):
                field = field[1:]
                sort_order = "DESC"
            
            if field == "balance":
                sort_fields.append(f"sum(position) {sort_order}")
            else:
                sort_fields.append(f"{field} {sort_order}")
        query += " ORDER BY " + ", ".join(sort_fields)

    return query


def format_output(output: list, args) -> list:
    """Formats the raw output from the BQL query into a pretty-printable list."""
    formatted_output = []
    
    # Initialize grand total dictionary to accumulate balances by currency
    grand_total = {}
    converted_total = 0
    
    for row in list(output): # Ensure output is a list of lists
        if not row:
            continue
        
        account_name = row[0]
        account_depth = account_name.count(':') + 1 # Calculate depth based on colons

        if args.depth and account_depth > args.depth:
            continue

        if args.zero and row[-1].is_empty():
            continue
            
        # Handle currency conversion
        if args.exchange:
            # When exchange currency is specified, we have an additional column with converted values
            balance_inventory = row[1]  # Original balance
            converted_inventory = row[2]  # Converted balance
            
            # Format original balance
            balance_parts = []
            for currency, amount in balance_inventory.items():
                # Check if the currency is a tuple and extract the string
                if isinstance(currency, tuple):
                    currency_str = currency[0]
                else:
                    currency_str = currency

                # Correctly access the number from the Position object's `units`
                formatted_value = "{:,.2f}".format(amount.units.number)
                
                balance_parts.append(f"{formatted_value} {currency_str}")
            
            formatted_balance = " ".join(balance_parts)
            
            # Format converted balance
            converted_amount = converted_inventory.get_currency_units(args.exchange)
            formatted_converted = "{:,.2f} {}".format(converted_amount.number, converted_amount.currency)
            
            # Accumulate for grand total
            if args.total:
                # Accumulate original currencies
                for currency, amount in balance_inventory.items():
                    # Check if the currency is a tuple and extract the string
                    if isinstance(currency, tuple):
                        currency_str = currency[0]
                    else:
                        currency_str = currency
                    
                    if currency_str in grand_total:
                        grand_total[currency_str] += amount.units.number
                    else:
                        grand_total[currency_str] = amount.units.number
                
                # Accumulate converted amount
                converted_total += converted_amount.number
            
            new_row = list(row)
            new_row[1] = formatted_balance
            new_row[2] = formatted_converted
            formatted_output.append(tuple(new_row))
        else:
            # The balance is always the last element in the row tuple
            balance_inventory = row[-1]
            
            # An Inventory object can contain multiple currencies. We need to iterate
            # through its items, which are (currency, Position) pairs.
            balance_parts = []
            for currency, amount in balance_inventory.items():
                # Check if the currency is a tuple and extract the string
                if isinstance(currency, tuple):
                    currency_str = currency[0]
                else:
                    currency_str = currency

                # Correctly access the number from the Position object's `units`
                formatted_value = "{:,.2f}".format(amount.units.number)
                
                balance_parts.append(f"{formatted_value} {currency_str}")
                
                # Accumulate for grand total
                if args.total:
                    if currency_str in grand_total:
                        grand_total[currency_str] += amount.units.number
                    else:
                        grand_total[currency_str] = amount.units.number
            
            formatted_balance = " ".join(balance_parts)
            
            new_row = list(row)
            new_row[-1] = formatted_balance
            formatted_output.append(tuple(new_row))

    # Add grand total row if requested
    if args.total and (grand_total or args.exchange):
        if args.exchange:
            # Format the grand total balances
            total_parts = []
            for currency, amount in grand_total.items():
                formatted_value = "{:,.2f}".format(amount)
                total_parts.append(f"{formatted_value} {currency}")
            
            formatted_total = " ".join(total_parts)
            formatted_converted_total = "{:,.2f} {}".format(converted_total, args.exchange)
            
            # Add a separator row and the total row
            if args.exchange:
                formatted_output.append(("-------------------", "-------------------", "-------------------"))
                formatted_output.append(("Total", formatted_total, formatted_converted_total))
            else:
                formatted_output.append(("-------------------", "-------------------"))
                formatted_output.append(("Total", formatted_total))
        else:
            # Format the grand total balances
            total_parts = []
            for currency, amount in grand_total.items():
                formatted_value = "{:,.2f}".format(amount)
                total_parts.append(f"{formatted_value} {currency}")
            
            formatted_total = " ".join(total_parts)
            # Add a separator row and the total row
            formatted_output.append(("-------------------", "-------------------"))
            formatted_output.append(("Total", formatted_total))

    return formatted_output


