"""
Test to verify that the register command respects the --limit parameter.
"""

from tests.test_utils import run_reg_command


def test_register_limit_basic():
    """Test that register command respects the --limit parameter."""
    # Run the register command with limit of 5
    result = run_reg_command(["--limit", "5"])
    
    # Verify the command executed successfully
    assert result.exit_code == 0
    
    # Count the number of data rows in the output
    # The output should have exactly 5 transaction rows plus header
    lines = result.output.split('\n')
    
    # Find the table section and count data rows
    table_data = []
    in_table = False
    for line in lines:
        if line.strip().startswith('+') and '---' in line:
            if not in_table:
                in_table = True
            else:
                break
        elif in_table and line.strip() and not line.strip().startswith('|'):
            continue
        elif in_table:
            table_data.append(line)
    
    # Count actual data rows (excluding header and separator)
    # Skip the first row if it's a header (contains column names)
    data_rows = []
    for line in table_data:
        if line.strip().startswith('|') and '---' not in line:
            # Skip header row (contains column names like "Date", "Account", etc.)
            if any(col in line for col in ['Date', 'Account', 'Payee', 'Narration', 'Amount']):
                continue
            data_rows.append(line)
    
    # Should have exactly 5 data rows when limit is 5
    assert len(data_rows) == 5, f"Expected 5 rows with --limit 5, got {len(data_rows)}"


def test_register_limit_with_account():
    """Test that register command respects --limit with account filter."""
    # Run the register command with limit of 3 and account filter
    result = run_reg_command(["Assets:Bank:Checking", "--limit", "3"])
    
    # Verify the command executed successfully
    assert result.exit_code == 0
    
    # Count the number of data rows in the output
    lines = result.output.split('\n')
    
    # Find the table section and count data rows
    table_data = []
    in_table = False
    for line in lines:
        if line.strip().startswith('+') and '---' in line:
            if not in_table:
                in_table = True
            else:
                break
        elif in_table and line.strip() and not line.strip().startswith('|'):
            continue
        elif in_table:
            table_data.append(line)
    
    # Count actual data rows (excluding header and separator)
    # Skip the first row if it's a header (contains column names)
    data_rows = []
    for line in table_data:
        if line.strip().startswith('|') and '---' not in line:
            # Skip header row (contains column names like "Date", "Account", etc.)
            if any(col in line for col in ['Date', 'Account', 'Payee', 'Narration', 'Amount']):
                continue
            data_rows.append(line)
    
    # Should have exactly 3 data rows when limit is 3
    assert len(data_rows) == 3, f"Expected 3 rows with --limit 3, got {len(data_rows)}"


def test_register_limit_with_sort():
    """Test that register command respects --limit with sorting."""
    # Run the register command with limit of 4 and sorting
    result = run_reg_command(["--limit", "4", "--sort", "-date"])
    
    # Verify the command executed successfully
    assert result.exit_code == 0
    
    # Count the number of data rows in the output
    lines = result.output.split('\n')
    
    # Find the table section and count data rows
    table_data = []
    in_table = False
    for line in lines:
        if line.strip().startswith('+') and '---' in line:
            if not in_table:
                in_table = True
            else:
                break
        elif in_table and line.strip() and not line.strip().startswith('|'):
            continue
        elif in_table:
            table_data.append(line)
    
    # Count actual data rows (excluding header and separator)
    # Skip the first row if it's a header (contains column names)
    data_rows = []
    for line in table_data:
        if line.strip().startswith('|') and '---' not in line:
            # Skip header row (contains column names like "Date", "Account", etc.)
            if any(col in line for col in ['Date', 'Account', 'Payee', 'Narration', 'Amount']):
                continue
            data_rows.append(line)
    
    # Should have exactly 4 data rows when limit is 4
    assert len(data_rows) == 4, f"Expected 4 rows with --limit 4, got {len(data_rows)}"


def test_register_limit_alias_r():
    """Test that register command alias 'r' respects --limit parameter."""
    from click.testing import CliRunner
    from ledger2bql.main import cli
    
    runner = CliRunner()
    result = runner.invoke(cli, ["r", "--limit", "2"])
    
    # Verify the command executed successfully
    assert result.exit_code == 0
    
    # Count the number of data rows in the output
    lines = result.output.split('\n')
    
    # Find the table section and count data rows
    table_data = []
    in_table = False
    for line in lines:
        if line.strip().startswith('+') and '---' in line:
            if not in_table:
                in_table = True
            else:
                break
        elif in_table and line.strip() and not line.strip().startswith('|'):
            continue
        elif in_table:
            table_data.append(line)
    
    # Count actual data rows (excluding header and separator)
    # Skip the first row if it's a header (contains column names)
    data_rows = []
    for line in table_data:
        if line.strip().startswith('|') and '---' not in line:
            # Skip header row (contains column names like "Date", "Account", etc.)
            if any(col in line for col in ['Date', 'Account', 'Payee', 'Narration', 'Amount']):
                continue
            data_rows.append(line)
    
    # Should have exactly 2 data rows when limit is 2
    assert len(data_rows) == 2, f"Expected 2 rows with --limit 2, got {len(data_rows)}"