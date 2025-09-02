'''
Tests for the Register command with total option.
'''
import io
import os
from contextlib import redirect_stdout
from unittest.mock import patch

from ledger2bql.ledger_reg_to_bql import main as reg_main

def extract_full_table(output_lines):
    """Extract the full table including headers and data rows."""
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
        # Include everything between the table borders
        for line in output_lines[start_index:end_index + 1]:
            table_data.append(line)
    
    return table_data

@patch('os.getenv')
def test_reg_with_total(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['reg', '--total']):
            # Act
            reg_main()
    
    # Assert
    output = f.getvalue()
    
    table_lines = extract_full_table(output.splitlines())
    table_output = "\n".join(table_lines)

    # Check that the Running Total column header is present
    assert "Running Total" in table_output
    
    # Check that some expected rows with running totals are present
    assert "1,000.00 EUR |    1,000.00 EUR" in table_output
    assert "-1,000.00 EUR |        0.00 EUR" in table_output
    
    # Check that some expected accounts are still present
    assert "Assets:Bank:Checking" in table_output
    assert "Expenses:Sweets" in table_output

@patch('os.getenv')
def test_reg_with_total_flag_short(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['reg', '-T']):
            # Act
            reg_main()
    
    # Assert
    output = f.getvalue()
    
    table_lines = extract_full_table(output.splitlines())
    table_output = "\n".join(table_lines)

    # Check that the Running Total column header is present
    assert "Running Total" in table_output