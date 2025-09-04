'''
Tests for the "not" keyword functionality.
'''
import os
from unittest.mock import patch

from tests.test_utils import run_bal_command, run_reg_command


@patch('os.getenv')
def test_bal_not_keyword(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    # Act
    result = run_bal_command(['not', 'bank'])
    
    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The output should contain accounts that are NOT bank accounts
    assert "Expenses:Food" in output
    assert "Expenses:Sweets" in output
    assert "Income:Salary" in output
    assert "Equity:Opening-Balances" in output
    
    # But should not contain bank accounts
    assert "Assets:Bank:Checking" not in output


@patch('os.getenv')
def test_bal_not_keyword_multiple_patterns(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    # Act
    result = run_bal_command(['not', 'bank', 'cash'])
    
    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The output should contain accounts that are neither bank nor cash accounts
    assert "Expenses:Food" in output
    assert "Expenses:Sweets" in output
    assert "Income:Salary" in output
    assert "Equity:Opening-Balances" in output
    
    # But should not contain bank or cash accounts
    assert "Assets:Bank:Checking" not in output
    assert "Assets:Cash:Pocket-Money" not in output
    assert "Assets:Cash:BAM" not in output
    assert "Assets:Cash:USD" not in output


@patch('os.getenv')
def test_bal_not_keyword_with_regular_filter(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    # Act
    result = run_bal_command(['assets', 'not', 'bank'])
    
    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The output should contain asset accounts that are NOT bank accounts
    assert "Assets:Cash:Pocket-Money" in output
    assert "Assets:Cash:BAM" in output
    assert "Assets:Cash:USD" in output
    
    # But should not contain bank accounts
    assert "Assets:Bank:Checking" not in output


@patch('os.getenv')
def test_reg_not_keyword(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    # Act
    result = run_reg_command(['not', 'bank'])
    
    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The output should contain transactions that are NOT for bank accounts
    assert "Expenses:Food" in output
    assert "Expenses:Sweets" in output
    assert "Income:Salary" in output
    assert "Equity:Opening-Balances" in output
    
    # But should not contain bank account transactions
    assert "Assets:Bank:Checking" not in output


@patch('os.getenv')
def test_reg_not_keyword_multiple_patterns(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    # Act
    result = run_reg_command(['not', 'bank', 'cash'])
    
    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The output should contain transactions that are neither bank nor cash accounts
    assert "Expenses:Food" in output
    assert "Expenses:Sweets" in output
    assert "Income:Salary" in output
    assert "Equity:Opening-Balances" in output
    
    # But should not contain bank or cash account transactions
    assert "Assets:Bank:Checking" not in output
    assert "Assets:Cash:Pocket-Money" not in output
    assert "Assets:Cash:BAM" not in output
    assert "Assets:Cash:USD" not in output


@patch('os.getenv')
def test_reg_not_keyword_with_regular_filter(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    # Act
    result = run_reg_command(['assets', 'not', 'bank'])
    
    # Assert
    assert result.exit_code == 0
    output = result.output
    
    # The output should contain asset transactions that are NOT bank accounts
    assert "Assets:Cash:Pocket-Money" in output
    assert "Assets:Cash:BAM" in output
    assert "Assets:Cash:USD" in output
    
    # But should not contain bank account transactions
    assert "Assets:Bank:Checking" not in output