'''
Test utilities for Click-based commands.
'''
import os
from click.testing import CliRunner
from dotenv import load_dotenv

from ledger2bql.main import cli

# Load environment variables from the tests directory
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path, override=True)

def run_bal_command(args=None):
    """Run the balance command with given arguments."""
    runner = CliRunner()
    if args is None:
        args = []
    return runner.invoke(cli, ['bal'] + args)

def run_reg_command(args=None):
    """Run the register command with given arguments."""
    runner = CliRunner()
    if args is None:
        args = []
    return runner.invoke(cli, ['reg'] + args)


def extract_table_data(output_lines):
    """Extract table data from output lines."""
    table_data = []
    start_index = -1
    end_index = -1

    for i, line in enumerate(output_lines):
        if line.strip().startswith("+") and "---" in line:
            if start_index == -1:
                start_index = i
            else:
                end_index = i
                break
    
    if start_index != -1 and end_index != -1:
        # The actual data starts after the header and separator lines
        for line in output_lines[start_index + 3:end_index]:
            table_data.append(line)
    
    return table_data