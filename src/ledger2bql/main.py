"""
CLI runner for Ledger2BQL utility.
"""
import sys
import re
from importlib.metadata import version, PackageNotFoundError
from dotenv import find_dotenv, load_dotenv
import click

from .ledger_bal_to_bql import main as bal_main
from .ledger_reg_to_bql import main as reg_main


def is_date_like_pattern(arg):
    """
    Check if an argument looks like a date range pattern.
    
    Returns True for arguments that:
    - Start with 4 digits (year) followed by optional date components
    - Contain '..' (date range separator)
    - Match common date formats like YYYY, YYYY-MM, YYYY-MM-DD
    
    Examples:
    - "2025" -> True
    - "2025-08" -> True
    - "2025..2026" -> True
    - "2025-08..2025-09" -> True
    - "Expenses" -> False
    - "bank" -> False
    """
    # Check if it starts with 4 digits (a year)
    if re.match(r'^\d{4}', arg):
        # Check if it's a valid date range pattern
        if '..' in arg:
            # Could be a range like "2025..2026" or "2025-08..2025-09"
            return True
        else:
            # Could be a single date like "2025" or "2025-08"
            # Check if it matches date patterns
            date_patterns = [
                r'^\d{4}$',  # YYYY
                r'^\d{4}-\d{2}$',  # YYYY-MM
                r'^\d{4}-\d{2}-\d{2}$'  # YYYY-MM-DD
            ]
            return any(re.match(pattern, arg) for pattern in date_patterns)
    return False


def preprocess_argv():
    """
    Preprocess sys.argv to automatically detect date-like patterns and convert them
    to explicit date-range arguments.
    
    This function modifies sys.argv in place to insert '-d' before date-like arguments.
    """
    if len(sys.argv) < 2:
        return
    
    # We don't want to process the command name (first argument after script name)
    command = sys.argv[1]
    args = sys.argv[2:]  # The rest of the arguments
    
    processed_args = []
    i = 0
    while i < len(args):
        arg = args[i]
        
        # If we find a date-like pattern, add -d before it
        if is_date_like_pattern(arg):
            processed_args.extend(['-d', arg])
        else:
            processed_args.append(arg)
        
        i += 1
    
    # Update sys.argv with the processed arguments
    sys.argv = [sys.argv[0], command] + processed_args


def main():
    """main entry point"""
    if len(sys.argv) < 2:
        try:
            v = version("ledger2bql")
        except PackageNotFoundError:
            v = "local"
        click.echo(f"ledger2bql v{v}")
        click.echo("Usage: ledger2bql [bal|b|reg|r] [options]")
        sys.exit(1)

    # Initialize environment variables by loading .env files in the 
    # parent directories.
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path, override=True)

    # Preprocess arguments to automatically detect date-like patterns
    preprocess_argv()

    command = sys.argv[1]
    sys.argv = sys.argv[1:]

    if command in ("bal", "b"):
        bal_main()
    elif command in ("reg", "r"):
        reg_main()
    else:
        click.echo(f"Unknown command: {command}")
        click.echo("Usage: ledger2bql [bal|b|reg|r] [options]")
        sys.exit(1)


if __name__ == "__main__":
    main()