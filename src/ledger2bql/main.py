"""
CLI runner for Ledger2BQL utility.
"""
import sys
from importlib.metadata import version, PackageNotFoundError
from dotenv import find_dotenv, load_dotenv

from .ledger_bal_to_bql import main as bal_main
from .ledger_reg_to_bql import main as reg_main


def main():
    """main entry point"""
    if len(sys.argv) < 2:
        try:
            v = version("ledger2bql")
        except PackageNotFoundError:
            v = "local"
        print(f"ledger2bql v{v}")
        print("Usage: ledger2bql [bal|b|reg|r] [options]")
        sys.exit(1)

    # Initialize environment variables by loading .env files in the 
    # parent directories.
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path, override=True)

    command = sys.argv[1]
    sys.argv = sys.argv[1:]

    if command in ("bal", "b"):
        bal_main()
    elif command in ("reg", "r"):
        reg_main()
    else:
        print(f"Unknown command: {command}")
        print("Usage: ledger2bql [bal|b|reg|r] [options]")
        sys.exit(1)

if __name__ == "__main__":
    main()
