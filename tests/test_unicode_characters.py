"""
Test for Unicode character handling in account names and payees.
"""
import os
import tempfile
from click.testing import CliRunner
from dotenv import load_dotenv

from ledger2bql.main import cli


# Load environment variables from the tests directory
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path, override=True)


def test_unicode_characters_in_account_names():
    """Test that Unicode characters in account names don't distort the table output."""
    # Create a temporary ledger file with Unicode characters in account names
    ledger_content = """
2023-01-01 open Assets:Bank:Račun
2023-01-01 open Expenses:Food

2023-01-01 * "Test Transaction with Unicode"
    Assets:Bank:Račun    100.00 EUR
    Expenses:Food    -100.00 EUR
"""
    
    runner = CliRunner()
    
    with runner.isolated_filesystem():
        # Create temporary ledger file
        with open('test_ledger.bean', 'w', encoding='utf-8') as f:
            f.write(ledger_content)
        
        # Set the BEANCOUNT_FILE environment variable
        os.environ['BEANCOUNT_FILE'] = 'test_ledger.bean'
        
        # Run the balance command
        result = runner.invoke(cli, ['bal'])
        
        # Verify the command executed successfully
        assert result.exit_code == 0
        
        # Verify that the table is properly formatted
        output_lines = result.output.split('\n')
        
        # Find the table lines (lines that start with |)
        table_lines = [line for line in output_lines if line.strip().startswith('|')]
        
        # Separate header/data lines from separator lines
        # In psql format, separator lines have fewer | characters
        data_lines = [line for line in table_lines if line.count('|') >= 3]  # Data rows
        separator_lines = [line for line in table_lines if line.count('|') < 3]  # Separator rows
        
        # Check if all data lines have the same number of columns
        data_column_counts = [line.count('|') for line in data_lines]
        
        # All data lines should have the same number of columns (3: empty, Account, Balance, empty)
        # If they don't, the table is distorted
        assert len(set(data_column_counts)) == 1, f"Table data is distorted. Column counts: {set(data_column_counts)}\nOutput:\n{result.output}"


def test_unicode_characters_in_payees():
    """Test that Unicode characters in payees don't distort the table output."""
    # Create a temporary ledger file with Unicode characters in payees
    ledger_content = """
2023-01-01 open Assets:Bank
2023-01-01 open Expenses:Utilities

2023-01-01 * "Račun za struju"
    Expenses:Utilities    80.00 EUR
    Assets:Bank    -80.00 EUR
"""
    
    runner = CliRunner()
    
    with runner.isolated_filesystem():
        # Create temporary ledger file
        with open('test_ledger.bean', 'w', encoding='utf-8') as f:
            f.write(ledger_content)
        
        # Set the BEANCOUNT_FILE environment variable
        os.environ['BEANCOUNT_FILE'] = 'test_ledger.bean'
        
        # Run the register command
        result = runner.invoke(cli, ['reg'])
        
        # Verify the command executed successfully
        assert result.exit_code == 0
        
        # Verify that the table is properly formatted
        output_lines = result.output.split('\n')
        
        # Find the table lines (lines that start with |)
        table_lines = [line for line in output_lines if line.strip().startswith('|')]
        
        # Separate header/data lines from separator lines
        # In psql format, separator lines have fewer | characters
        data_lines = [line for line in table_lines if line.count('|') >= 5]  # Data rows
        separator_lines = [line for line in table_lines if line.count('|') < 5]  # Separator rows
        
        # Check if all data lines have the same number of columns
        data_column_counts = [line.count('|') for line in data_lines]
        
        # All data lines should have the same number of columns (6: empty, Date, Account, Payee, Narration, Amount, empty)
        # If they don't, the table is distorted
        assert len(set(data_column_counts)) == 1, f"Table data is distorted. Column counts: {set(data_column_counts)}\nOutput:\n{result.output}"