"""
A command-line tool to execute named queries from the Beancount ledger file.
"""

import click
import beancount.loader
import beancount.core.data
from .utils import get_beancount_file_path, execute_bql_command_with_click


@click.command(name="query", short_help="[q] Execute a named query from the ledger")
@click.argument("query_name")
@click.option("--no-pager", is_flag=True, help="Disable automatic paging of output.")
def query_command(query_name, no_pager):
    """Execute a named query from the ledger file."""

    # Package arguments in a way compatible with the existing code
    class Args:
        def __init__(self, query_name, no_pager):
            self.query_name = query_name
            self.no_pager = no_pager

    args = Args(query_name, no_pager)

    # Execute the command
    execute_bql_command_with_click(
        parse_query, format_output, [], [], args, command_type="query"
    )


def parse_query(args):
    """Parse the query name and retrieve the actual BQL query from the ledger."""
    beancount_file = get_beancount_file_path()

    # Load the beancount file using the beancount library
    entries, errors, options_map = beancount.loader.load_file(beancount_file)

    # Look for query entries
    query_entries = [
        entry for entry in entries if isinstance(entry, beancount.core.data.Query)
    ]

    # Try to find an exact match first
    for query_entry in query_entries:
        if query_entry.name == args.query_name:
            return query_entry.query_string

    # Try case-insensitive match
    for query_entry in query_entries:
        if query_entry.name.lower() == args.query_name.lower():
            # Store the actual query name for display
            args.actual_query_name = query_entry.name
            return query_entry.query_string

    # Try partial matching - look for queries that contain the search term
    for query_entry in query_entries:
        if args.query_name.lower() in query_entry.name.lower():
            # Store the actual query name for display
            args.actual_query_name = query_entry.name
            return query_entry.query_string

    # If no match found, raise an error
    raise ValueError(f"Query '{args.query_name}' not found in the ledger file.")


def format_output(output: list, args) -> list:
    """Format the raw output from the BQL query into a pretty-printable list."""
    # For queries, we want to display all columns as they are returned
    formatted_output = []

    for row in output:
        # Convert each field to a string representation
        formatted_row = []
        for field in row:
            if hasattr(field, "__dict__") and hasattr(field, "units"):
                # This is likely a Position or Amount object
                if hasattr(field.units, "number") and hasattr(field.units, "currency"):
                    formatted_row.append(f"{field.units.number} {field.units.currency}")
                else:
                    formatted_row.append(str(field))
            elif isinstance(field, (str, int, float)):
                formatted_row.append(str(field))
            else:
                formatted_row.append(str(field))
        formatted_output.append(formatted_row)

    return formatted_output
