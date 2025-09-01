"""
CLI runner for Ledger2BQL utility.
"""
import sys

from .ledger_bal_to_bql import main as bal_main
from .ledger_reg_to_bql import main as reg_main

def main():
    """main entry point"""
    if len(sys.argv) < 2:
        print("Usage: ledger2bql [bal|b|reg|r] [options]")
        sys.exit(1)

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
