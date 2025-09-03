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
  python ledger_to_bql.py Expenses -b 2024-01-01 -e 2024-02-01

  # Translate a command with multiple account filters.
  # This is equivalent to `ledger bal income expenses`
  python ledger_to_bql.py income expenses

  # Translate a command to show a grand total row.
  # This is equivalent to `ledger bal --total`
  python ledger_to_bql.py --total

Key Mappings:
  - `--depth X` or `-d X` -> `GROUP BY level(account) <= X`
  - `--zero` or `-Z`       -> `WHERE balance != 0` (removes accounts with zero balance)
  - `--begin DATE` or `-b DATE` -> `WHERE date >= "DATE"`
  - `--end DATE` or `-e DATE`   -> `WHERE date < "DATE"`
  - `--total` or `-T`           -> Show a grand total row at the end
  - `ACCOUNT_REGEX`           -> `WHERE account ~ "ACCOUNT_REGEX"`
  - `@DESCRIPTION_REGEX   -> `WHERE description ~ "DESCRIPTION_REGEX"`
"""

import argparse
from .date_parser import parse_date, parse_date_range
from .utils import add_common_arguments, execute_bql_command, parse_amount_filter


def create_parser():
    '''Define the query parser'''
    parser = argparse.ArgumentParser(
        description="Translate ledger-cli balance command arguments to a Beanquery (BQL) query.",
        epilog="""
        Note: The `--empty` flag from ledger-cli is generally not needed for BQL
        as `bean-query` typically includes all accounts by default.
        """
    )

    add_common_arguments(parser)

    parser.add_argument(
        '--depth', '-D',
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

    if args.begin:
        begin_date = parse_date(args.begin)
        where_clauses.append(f'date >= date("{begin_date}")')
    if args.end:
        end_date = parse_date(args.end)
        where_clauses.append(f'date < date("{end_date}")')
    
    # Handle date range if provided
    if args.date_range:
        begin_date, end_date = parse_date_range(args.date_range)
        if begin_date:
            where_clauses.append(f'date >= date("{begin_date}")')
        if end_date:
            where_clauses.append(f'date < date("{end_date}")')

    # Handle amount filters
    if args.amount:
        for amount_filter in args.amount:
            op, val, cur = parse_amount_filter(amount_filter)
            amount_clause = f"number {op} {val}"
            if cur:
                amount_clause += f" AND currency = '{cur}'"
            where_clauses.append(amount_clause)
    
    # Handle currency filter
    if args.currency:
        if isinstance(args.currency, list):
            currencies_str = "', '".join(args.currency)
            where_clauses.append(f"currency IN ('{currencies_str}')")
        else:
            where_clauses.append(f"currency = '{args.currency}'")

    # Build the final query
    select_clause = "SELECT account, units(sum(position)) as Balance"
    query = select_clause

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    if group_by_clauses:
        query += " GROUP BY " + ", ".join(group_by_clauses)

    if args.sort:
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
    
    for row in list(output): # Ensure output is a list of lists
        if not row:
            continue
        
        account_name = row[0]
        account_depth = account_name.count(':') + 1 # Calculate depth based on colons

        if args.depth and account_depth > args.depth:
            continue

        if args.zero and row[-1].is_empty():
            continue
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
    if args.total and grand_total:
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


def main():
    """Runs the given query and prints the output in a pretty format."""
    # Determine headers for the table
    headers = ["Account", "Balance"]
    alignments = ["left", "right"]
    
    # Pass args.depth to format_output_func via kwargs
    execute_bql_command(create_parser, parse_query, format_output, 
                        headers, alignments, command_type='bal')


if __name__ == '__main__':
    main()