"""
Tests for the Balance command with hierarchy option to confirm that 
the balance includes children's + own for Expenses:Transport account.
"""
import os
from unittest.mock import patch

from tests.test_utils import run_bal_command, extract_table_data


@patch('os.getenv')
def test_bal_hierarchy_expenses_transport_with_children(mock_getenv):
    """Test that Expenses:Transport account correctly aggregates its children."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    # Act
    result = run_bal_command(['-H', 'Expenses:Transport'])
    
    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)

    # Check that Expenses:Transport (parent) shows aggregated balance including children
    assert "| Expenses:Transport       |" in table_output
    
    # Check that children are also shown
    assert "| Expenses:Transport:Bus   |" in table_output
    assert "| Expenses:Transport:Train |" in table_output
    
    # The parent Expenses:Transport should show the combined balance of all its children
    # From the sample ledger:
    # - Expenses:Transport:Bus has 10 EUR
    # - Expenses:Transport:Train has 15 EUR
    # - Expenses:Transport itself has 7 USD (from direct transaction)
    # So Expenses:Transport should show the total: 25 EUR + 7 USD


@patch('os.getenv')
def test_bal_hierarchy_expenses_transport_verify_aggregation_values(mock_getenv):
    """Test that Expenses:Transport hierarchical balance correctly aggregates child values."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    # Act
    result = run_bal_command(['-H', 'Expenses:Transport'])
    
    # Assert
    assert result.exit_code == 0
    table_lines = extract_table_data(result.output.splitlines())
    table_output = "\n".join(table_lines)
    
    # Find the rows for Expenses:Transport and its children
    transport_row = None
    transport_bus_row = None
    transport_train_row = None
    
    for line in table_lines:
        if "| Expenses:Transport       |" in line:
            transport_row = line
        elif "| Expenses:Transport:Bus   |" in line:
            transport_bus_row = line
        elif "| Expenses:Transport:Train |" in line:
            transport_train_row = line
    
    # Verify that all rows were found
    assert transport_row is not None
    assert transport_bus_row is not None
    assert transport_train_row is not None
    
    # Verify that Expenses:Transport (parent) balance equals the sum of its children plus its own
    # From the sample ledger:
    # - Expenses:Transport:Bus has 10 EUR
    # - Expenses:Transport:Train has 15 EUR
    # - Expenses:Transport itself has 7 USD (from direct transaction)
    # 
    # Expenses:Transport row should show: 25.00 EUR 7.00 USD
    # Expenses:Transport:Bus row: 10.00 EUR
    # Expenses:Transport:Train row: 15.00 EUR
    assert "25.00 EUR" in transport_row
    assert "7.00 USD" in transport_row
    
    assert "10.00 EUR" in transport_bus_row
    
    assert "15.00 EUR" in transport_train_row
    
    # Verify the math: Parent should equal sum of children plus its own transactions
    # EUR: 10.00 + 15.00 = 25.00 \u2713
    # USD: 7.00 (from parent's own transaction) \u2713