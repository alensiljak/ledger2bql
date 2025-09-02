'''
Tests for the Balance command with total option.
'''
import io
import os
from contextlib import redirect_stdout
from unittest.mock import patch

from ledger2bql.ledger_bal_to_bql import main as bal_main

def extract_table_data(output_lines):
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

@patch('os.getenv')
def test_bal_with_total(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', '--total']):
            # Act
            bal_main()
    
    # Assert
    output = f.getvalue()
    
    table_lines = extract_table_data(output.splitlines())
    table_output = "\n".join(table_lines)

    # Check that the total row is present
    assert "| Total" in table_output
    
    # Check that some expected accounts are still present
    assert "Assets:Bank:Checking" in table_output
    assert "Expenses:Sweets" in table_output

    # Check that the separator row is NOT present (it should be filtered out)
    assert "| ------------------- | ------------------- |" not in table_output

@patch('os.getenv')
def test_bal_with_total_flag_short(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', '-T']):
            # Act
            bal_main()
    
    # Assert
    output = f.getvalue()
    
    table_lines = extract_table_data(output.splitlines())
    table_output = "\n".join(table_lines)

    # Check that the total row is present
    assert "| Total" in table_output

    # Check that some expected accounts are still present
    assert "Assets:Bank:Checking" in table_output
    assert "Expenses:Sweets" in table_output

    # Check that the separator row is NOT present (it should be filtered out)
    assert "| ------------------- | ------------------- |" not in table_output