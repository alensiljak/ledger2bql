"""
A command-line tool to translate ledger-cli 'balance' command syntax
into a Beanquery (BQL) query.
"""

import click
from .date_parser import parse_date, parse_date_range
from .utils import (
    add_common_click_arguments,
    execute_bql_command_with_click,
    parse_account_params,
    parse_account_pattern,
    parse_amount_filter,
)


@click.command(name="bal", short_help="[b] Show account balances")
@click.option(
    "--depth",
    "-D",
    type=int,
    help="Show accounts up to a certain depth (level) in the account tree.",
)
@click.option(
    "--zero", "-Z", is_flag=True, help="Exclude accounts with a zero balance."
)
@click.option(
    "--hierarchy",
    "-H",
    is_flag=True,
    help="Show hierarchical view with parent accounts aggregated.",
)

@click.argument("account_regex", nargs=-1)
@add_common_click_arguments
def bal_command(account_regex, depth, zero, hierarchy, sort=None, **kwargs):
    """Translate ledger-cli balance command arguments to a Beanquery (BQL) query."""
    # Apply default sorting for balance command if no sort is specified
    if sort is None:
        sort = "account"

    # Package arguments in a way compatible with the existing code
    class Args:
        def __init__(self, account_regex, depth, zero, hierarchy, sort=None, **kwargs):
            self.account_regex = account_regex
            self.depth = depth
            self.zero = zero
            self.hierarchy = hierarchy
            self.sort = sort
            for key, value in kwargs.items():
                setattr(self, key, value)

    args = Args(account_regex, depth, zero, hierarchy, sort=sort, **kwargs)

    # Determine headers for the table
    headers = ["Account", "Balance"]
    alignments = ["left", "right"]

    # Execute the command
    execute_bql_command_with_click(
        parse_query, format_output, headers, alignments, args, command_type="bal"
    )


def parse_query(args):
    """Parse Ledger query into BQL"""
    where_clauses = []
    group_by_clauses = []

    # Handle account regular expressions and payee filters
    account_regexes, excluded_account_regexes, payee_where_clauses = (
        parse_account_params(args.account_regex)
    )
    where_clauses.extend(payee_where_clauses)

    if account_regexes:
        for pattern in account_regexes:
            regex_pattern = parse_account_pattern(pattern)
            where_clauses.append(f"account ~ '{regex_pattern}'")

    if excluded_account_regexes:
        for pattern in excluded_account_regexes:
            regex_pattern = parse_account_pattern(pattern)
            where_clauses.append(f"NOT (account ~ '{regex_pattern}')")

    if hasattr(args, "begin") and args.begin:
        begin_date = parse_date(args.begin)
        where_clauses.append(f'date >= date("{begin_date}")')
    if hasattr(args, "end") and args.end:
        end_date = parse_date(args.end)
        where_clauses.append(f'date < date("{end_date}")')

    # Handle date range if provided
    if hasattr(args, "date_range") and args.date_range:
        begin_date, end_date = parse_date_range(args.date_range)
        if begin_date:
            where_clauses.append(f'date >= date("{begin_date}")')
        if end_date:
            where_clauses.append(f'date < date("{end_date}")')

    # Handle amount filters
    if hasattr(args, "amount") and args.amount:
        # NEW APPROACH: Don't apply amount filters in the BQL query
        # Instead, we'll fetch all accounts and filter the aggregated results in Python
        # This ensures that amount filters are applied to final balances, not individual transactions
        amount_filters = []
        for amount_filter in args.amount:
            op, val, cur = parse_amount_filter(amount_filter)
            amount_filters.append((op, val, cur))
        # Store for use in format_output
        args.amount_filters = amount_filters
        # Don't add amount filters to where_clauses - we'll handle them in post-processing

    # Handle currency filter
    if hasattr(args, "currency") and args.currency:
        if isinstance(args.currency, list):
            currencies_str = "', '".join(args.currency)
            where_clauses.append(f"currency IN ('{currencies_str}')")
        else:
            where_clauses.append(f"currency = '{args.currency}'")

    # Build the final query

    
    # Original logic for building the query
    if hasattr(args, "exchange") and args.exchange:
        # When exchange currency is specified, convert all positions to that currency
        select_clause = f"SELECT account, units(sum(position)) as Balance, convert(sum(position), '{args.exchange}') as Converted"
    else:
        select_clause = "SELECT account, units(sum(position)) as Balance"
    query = select_clause

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    if group_by_clauses:
        query += " GROUP BY " + ", ".join(group_by_clauses)

    if hasattr(args, "sort") and args.sort:
        sort_fields = []
        for field in args.sort.split(","):
            field = field.strip()
            sort_order = "ASC"
            if field.startswith("-"):
                field = field[1:]
                sort_order = "DESC"

            if field == "balance":
                sort_fields.append(f"sum(position) {sort_order}")
            else:
                sort_fields.append(f"{field} {sort_order}")
        query += " ORDER BY " + ", ".join(sort_fields)

    # Handle limit
    if hasattr(args, "limit") and args.limit:
        query += f" LIMIT {args.limit}"

    return query


def format_output(output: list, args) -> list:
    """Formats the raw output from the BQL query into a pretty-printable list."""
    formatted_output = []

    # Initialize grand total dictionary to accumulate balances by currency
    grand_total = {}
    converted_total = 0

    # Apply amount filters to the aggregated results if present
    if hasattr(args, "amount_filters") and args.amount_filters:
        filtered_output = []
        for row in output:
            if not row:
                continue
            
            # Get the balance inventory (last column for non-exchange, second-to-last for exchange)
            if hasattr(args, "exchange") and args.exchange:
                balance_inventory = row[1]  # Balance column
            else:
                balance_inventory = row[-1]  # Last column
            
            # Check if this account meets all amount filter criteria
            meets_all_filters = True
            for op, val, cur in args.amount_filters:
                filter_met = False
                
                # Check each currency position in the balance
                for currency, amount in balance_inventory.items():
                    # Extract currency string
                    if isinstance(currency, tuple):
                        currency_str = currency[0]
                    else:
                        currency_str = currency
                    
                    # Extract number
                    number = amount.units.number
                    

                    
                    # Check if currency matches (if specified)
                    if cur and currency_str != cur:
                        continue
                    
                    # Check the amount condition
                    if op == ">" and number > val:
                        filter_met = True
                        break
                    elif op == ">=" and number >= val:
                        filter_met = True
                        break
                    elif op == "<" and number < val:
                        filter_met = True
                        break
                    elif op == "<=" and number <= val:
                        filter_met = True
                        break
                    elif op == "=" and number == val:
                        filter_met = True
                        break
                

                
                if not filter_met:
                    meets_all_filters = False
                    break
            
            if meets_all_filters:
                filtered_output.append(row)
        
        output = filtered_output

    # Handle hierarchical view if requested
    if hasattr(args, "hierarchy") and args.hierarchy:
        # Create hierarchical view: show parent accounts with their aggregated balances
        from collections import defaultdict
        from decimal import Decimal

        # Dictionary to store balances for parent accounts
        parent_balances = defaultdict(lambda: defaultdict(Decimal))
        parent_converted = defaultdict(Decimal) if args.exchange else None

        # First, collect all individual account balances and compute parent balances
        individual_rows = {}
        # Keep track of which accounts exist as individual accounts
        individual_accounts = set()

        for row in list(output):  # Ensure output is a list of lists
            if not row:
                continue

            account_name = row[0]
            individual_rows[account_name] = row
            individual_accounts.add(account_name)

            # Compute balances for all parent accounts
            parts = account_name.split(":")

            # For each level of the hierarchy, add this account's balance
            for i in range(
                len(parts) - 1
            ):  # Don't include the account itself, only parents
                parent_account = ":".join(parts[: i + 1])

                # Handle currency conversion and balance aggregation
                if args.exchange:
                    # When exchange currency is specified, we have an additional column with converted values
                    balance_inventory = row[1]  # Original balance

                    # Sum original balances by currency
                    if hasattr(
                        balance_inventory, "items"
                    ):  # It's an inventory with multiple currencies
                        for currency, amount in balance_inventory.items():
                            # Extract currency string
                            if isinstance(currency, tuple):
                                currency_str = currency[0]
                            else:
                                currency_str = currency

                            # Extract number (handle Decimal)
                            number = amount.units.number

                            # Add to parent balance
                            parent_balances[parent_account][currency_str] += number

                    # For converted balances, we need to get the converted value for this specific row
                    converted_inventory = row[2]  # Converted balance
                    converted_amount = converted_inventory.get_currency_units(
                        args.exchange
                    )
                    parent_converted[parent_account] += converted_amount.number
                else:
                    # The balance is always the last element in the row tuple
                    balance_inventory = row[-1]

                    # Sum balances by currency
                    if hasattr(
                        balance_inventory, "items"
                    ):  # It's an inventory with multiple currencies
                        for currency, amount in balance_inventory.items():
                            # Extract currency string
                            if isinstance(currency, tuple):
                                currency_str = currency[0]
                            else:
                                currency_str = currency

                            # Extract number (handle Decimal)
                            number = amount.units.number

                            # Add to parent balance
                            parent_balances[parent_account][currency_str] += number

        # Now, for accounts that exist as individual accounts, also add their own balances to their aggregated balances
        for account_name in individual_accounts:
            # Handle currency conversion and balance aggregation for the account's own balance
            row = individual_rows[account_name]
            if args.exchange:
                # When exchange currency is specified, we have an additional column with converted values
                balance_inventory = row[1]  # Original balance

                # Sum original balances by currency
                if hasattr(
                    balance_inventory, "items"
                ):  # It's an inventory with multiple currencies
                    for currency, amount in balance_inventory.items():
                        # Extract currency string
                        if isinstance(currency, tuple):
                            currency_str = currency[0]
                        else:
                            currency_str = currency

                        # Extract number (handle Decimal)
                        number = amount.units.number

                        # Add to the account's own aggregated balance
                        parent_balances[account_name][currency_str] += number

                # For converted balances, we need to get the converted value for this specific row
                converted_inventory = row[2]  # Converted balance
                converted_amount = converted_inventory.get_currency_units(args.exchange)
                parent_converted[account_name] += converted_amount.number
            else:
                # The balance is always the last element in the row tuple
                balance_inventory = row[-1]

                # Sum balances by currency
                if hasattr(
                    balance_inventory, "items"
                ):  # It's an inventory with multiple currencies
                    for currency, amount in balance_inventory.items():
                        # Extract currency string
                        if isinstance(currency, tuple):
                            currency_str = currency[0]
                        else:
                            currency_str = currency

                        # Extract number (handle Decimal)
                        number = amount.units.number

                        # Add to the account's own aggregated balance
                        parent_balances[account_name][currency_str] += number

        # Create combined output with both individual accounts and parent aggregates
        combined_output = []

        # Collect all unique account names (both individual and parents)
        all_accounts = set()
        all_accounts.update(individual_rows.keys())
        all_accounts.update(parent_balances.keys())

        # Sort accounts to show them in a logical order
        sorted_accounts = sorted(all_accounts)

        for account_name in sorted_accounts:
            # For all accounts, use the aggregated balances which include:
            # 1. The account's own balance (if it exists as an individual account)
            # 2. The sum of all its children's balances
            if account_name in parent_balances:
                # This account has aggregated balances (either it's a parent or it has children)
                currencies = parent_balances[account_name]
                if args.exchange:
                    # Create a mock inventory for the original balances
                    class MockInventory:
                        def __init__(self, currency_amounts):
                            self.currency_amounts = currency_amounts

                        def items(self):
                            # Return list of (currency, MockPosition) tuples
                            result = []
                            for currency, amount in self.currency_amounts.items():
                                result.append(
                                    ((currency, None), MockPosition(amount, currency))
                                )
                            return result

                        def is_empty(self):
                            return not self.currency_amounts

                    class MockPosition:
                        def __init__(self, amount, currency):
                            self.units = MockUnits(amount, currency)

                    class MockUnits:
                        def __init__(self, amount, currency):
                            self.number = amount
                            self.currency = currency

                    # Create a mock converted inventory
                    class MockConvertedInventory:
                        def __init__(self, amount):
                            self.amount = amount

                        def get_currency_units(self, currency):
                            class MockConvertedAmount:
                                def __init__(self, number, currency):
                                    self.number = number
                                    self.currency = currency

                            return MockConvertedAmount(self.amount, currency)

                    row = (
                        account_name,
                        MockInventory(currencies),
                        MockConvertedInventory(parent_converted[account_name]),
                    )
                else:
                    # Create a mock inventory for the balances
                    class MockInventory:
                        def __init__(self, currency_amounts):
                            self.currency_amounts = currency_amounts

                        def items(self):
                            # Return list of (currency, MockPosition) tuples
                            result = []
                            for currency, amount in self.currency_amounts.items():
                                result.append(
                                    ((currency, None), MockPosition(amount, currency))
                                )
                            return result

                        def is_empty(self):
                            return not self.currency_amounts

                    class MockPosition:
                        def __init__(self, amount, currency):
                            self.units = MockUnits(amount, currency)

                    class MockUnits:
                        def __init__(self, amount, currency):
                            self.number = amount
                            self.currency = currency

                    row = (account_name, MockInventory(currencies))
                combined_output.append(row)
            else:
                # This is a leaf account with no children, use its original data
                combined_output.append(individual_rows[account_name])

        output = combined_output

    # Handle depth collapsing (this should work for both regular and summarized output)
    if hasattr(args, "depth") and args.depth:
        # Group accounts by their parent at the specified depth level and sum balances
        from collections import defaultdict
        from decimal import Decimal

        # Dictionary to store collapsed balances: {parent_account: {currency: amount}}
        collapsed_balances = defaultdict(lambda: defaultdict(Decimal))
        collapsed_converted = defaultdict(Decimal) if args.exchange else None

        for row in list(output):  # Ensure output is a list of lists
            if not row:
                continue

            account_name = row[0]

            # Determine the parent account name for collapsing based on depth level
            parts = account_name.split(":")
            if len(parts) > args.depth:
                # Collapse to the specified level
                collapsed_account = ":".join(parts[: args.depth])
            else:
                collapsed_account = (
                    account_name  # Keep as is if already at or below collapse level
                )

            # Handle currency conversion and balance summarization
            if args.exchange:
                # When exchange currency is specified, we have an additional column with converted values
                balance_inventory = row[1]  # Original balance
                converted_inventory = row[2]  # Converted balance

                # Sum original balances by currency
                if hasattr(
                    balance_inventory, "items"
                ):  # It's an inventory with multiple currencies
                    for currency, amount in balance_inventory.items():
                        # Extract currency string
                        if isinstance(currency, tuple):
                            currency_str = currency[0]
                        else:
                            currency_str = currency

                        # Extract number (handle Decimal)
                        number = amount.units.number

                        # Add to collapsed balance
                        collapsed_balances[collapsed_account][currency_str] += number

                # Sum converted balances
                converted_amount = converted_inventory.get_currency_units(args.exchange)
                collapsed_converted[collapsed_account] += converted_amount.number
            else:
                # The balance is always the last element in the row tuple
                balance_inventory = row[-1]

                # Sum balances by currency
                if hasattr(
                    balance_inventory, "items"
                ):  # It's an inventory with multiple currencies
                    for currency, amount in balance_inventory.items():
                        # Extract currency string
                        if isinstance(currency, tuple):
                            currency_str = currency[0]
                        else:
                            currency_str = currency

                        # Extract number (handle Decimal)
                        number = amount.units.number

                        # Add to collapsed balance
                        collapsed_balances[collapsed_account][currency_str] += number

        # Convert the collapsed data back to the format expected by the rest of the function
        output = []
        for collapsed_account, currencies in collapsed_balances.items():
            if args.exchange:
                # Create a mock inventory for the original balances
                class MockInventory:
                    def __init__(self, currency_amounts):
                        self.currency_amounts = currency_amounts

                    def items(self):
                        # Return list of (currency, MockPosition) tuples
                        result = []
                        for currency, amount in self.currency_amounts.items():
                            result.append(
                                ((currency, None), MockPosition(amount, currency))
                            )
                        return result

                    def is_empty(self):
                        return not self.currency_amounts

                class MockPosition:
                    def __init__(self, amount, currency):
                        self.units = MockUnits(amount, currency)

                class MockUnits:
                    def __init__(self, amount, currency):
                        self.number = amount
                        self.currency = currency

                # Create a mock converted inventory
                class MockConvertedInventory:
                    def __init__(self, amount):
                        self.amount = amount

                    def get_currency_units(self, currency):
                        class MockConvertedAmount:
                            def __init__(self, number, currency):
                                self.number = number
                                self.currency = currency

                        return MockConvertedAmount(self.amount, currency)

                row = (
                    collapsed_account,
                    MockInventory(currencies),
                    MockConvertedInventory(collapsed_converted[collapsed_account]),
                )
            else:
                # Create a mock inventory for the balances
                class MockInventory:
                    def __init__(self, currency_amounts):
                        self.currency_amounts = currency_amounts

                    def items(self):
                        # Return list of (currency, MockPosition) tuples
                        result = []
                        for currency, amount in self.currency_amounts.items():
                            result.append(
                                ((currency, None), MockPosition(amount, currency))
                            )
                        return result

                    def is_empty(self):
                        return not self.currency_amounts

                class MockPosition:
                    def __init__(self, amount, currency):
                        self.units = MockUnits(amount, currency)

                class MockUnits:
                    def __init__(self, amount, currency):
                        self.number = amount
                        self.currency = currency

                row = (collapsed_account, MockInventory(currencies))
            output.append(row)

    # If using hierarchy, determine the minimum depth for total calculation
    min_depth = None
    if hasattr(args, "hierarchy") and args.hierarchy and args.total:
        # Find the minimum depth among all accounts
        depths = [row[0].count(":") + 1 for row in output if row]
        if depths:
            min_depth = min(depths)

    for row in list(output):  # Ensure output is a list of lists
        if not row:
            continue

        account_name = row[0]
        account_depth = account_name.count(":") + 1  # Calculate depth based on colons

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
            formatted_converted = "{:,.2f} {}".format(
                converted_amount.number, converted_amount.currency
            )

            # Accumulate for grand total
            if args.total:
                # When using hierarchy, only include accounts at the minimum depth to avoid double-counting
                should_include_in_total = True
                if (
                    hasattr(args, "hierarchy")
                    and args.hierarchy
                    and min_depth is not None
                ):
                    should_include_in_total = account_depth == min_depth

                if should_include_in_total:
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
                    # When using hierarchy, only include accounts at the minimum depth to avoid double-counting
                    should_include_in_total = True
                    if (
                        hasattr(args, "hierarchy")
                        and args.hierarchy
                        and min_depth is not None
                    ):
                        should_include_in_total = account_depth == min_depth

                    if should_include_in_total:
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
            formatted_converted_total = "{:,.2f} {}".format(
                converted_total, args.exchange
            )

            # Add a separator row and the total row
            if args.exchange:
                formatted_output.append(
                    (
                        "-------------------",
                        "-------------------",
                        "-------------------",
                    )
                )
                formatted_output.append(
                    ("Total", formatted_total, formatted_converted_total)
                )
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
