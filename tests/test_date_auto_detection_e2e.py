"""
End-to-end tests for the automatic date range detection functionality.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import io
from contextlib import redirect_stdout
from unittest.mock import patch

from ledger2bql.main import main as main_entry


@patch('os.getenv')
def test_bal_auto_date_range_detection(mock_getenv):
    """Test that date ranges starting with numbers are automatically detected."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    # Save original sys.argv
    original_argv = sys.argv
    
    try:
        # Set sys.argv to simulate command line arguments
        sys.argv = ['ledger2bql', 'bal', '2025']
        
        f = io.StringIO()
        with redirect_stdout(f):
            # Act
            try:
                main_entry()
            except SystemExit:
                pass  # argparse calls sys.exit() on error, which is expected in tests
        
        # Assert
        output = f.getvalue()
        # Check that the query contains date filtering
        assert 'date >= date("2025-01-01")' in output
        assert 'date < date("2026-01-01")' in output
        # Check that we have results (not "No records found")
        assert 'No records found.' not in output
        # Check that we have account data
        assert 'Assets:Bank:Checking' in output
        
    finally:
        # Restore original sys.argv
        sys.argv = original_argv


@patch('os.getenv')
def test_reg_auto_date_range_detection(mock_getenv):
    """Test that date ranges starting with numbers are automatically detected in register command."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    # Save original sys.argv
    original_argv = sys.argv
    
    try:
        # Set sys.argv to simulate command line arguments - use a date range with transactions
        sys.argv = ['ledger2bql', 'reg', '2025-03']
        
        f = io.StringIO()
        with redirect_stdout(f):
            # Act
            try:
                main_entry()
            except SystemExit:
                pass  # argparse calls sys.exit() on error, which is expected in tests
        
        # Assert
        output = f.getvalue()
        # Check that the query contains date filtering
        assert 'date >= date("2025-03-01")' in output
        assert 'date < date("2025-04-01")' in output
        # Check that we have results (not "No records found")
        assert 'No records found.' not in output
        # Check that we have transaction data
        assert 'Grocery Store' in output
        assert '2025-03-01' in output
        
    finally:
        # Restore original sys.argv
        sys.argv = original_argv


@patch('os.getenv')
def test_bal_auto_date_range_with_account_filter(mock_getenv):
    """Test that date ranges and account filters can be used together."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    # Save original sys.argv
    original_argv = sys.argv
    
    try:
        # Set sys.argv to simulate command line arguments
        sys.argv = ['ledger2bql', 'bal', '2025', 'Expenses']
        
        f = io.StringIO()
        with redirect_stdout(f):
            # Act
            try:
                main_entry()
            except SystemExit:
                pass  # argparse calls sys.exit() on error, which is expected in tests
        
        # Assert
        output = f.getvalue()
        # Check that the query contains both date filtering and account filtering
        assert 'date >= date("2025-01-01")' in output
        assert 'date < date("2026-01-01")' in output
        assert "account ~ 'Expenses'" in output
        # Check that we have results (not "No records found")
        assert 'No records found.' not in output
        # Check that we only have expense accounts
        assert 'Expenses:' in output
        assert 'Assets:Bank:Checking' not in output  # Should not have asset accounts
        
    finally:
        # Restore original sys.argv
        sys.argv = original_argv


@patch('os.getenv')
def test_bal_auto_date_range_with_range_syntax(mock_getenv):
    """Test that date ranges with .. syntax work correctly."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    # Save original sys.argv
    original_argv = sys.argv
    
    try:
        # Set sys.argv to simulate command line arguments
        sys.argv = ['ledger2bql', 'bal', '2025-01..2025-04']
        
        f = io.StringIO()
        with redirect_stdout(f):
            # Act
            try:
                main_entry()
            except SystemExit:
                pass  # argparse calls sys.exit() on error, which is expected in tests
        
        # Assert
        output = f.getvalue()
        # Check that the query contains date filtering
        assert 'date >= date("2025-01-01")' in output
        assert 'date < date("2025-04-01")' in output
        # Check that we have results (not "No records found")
        assert 'No records found.' not in output
        
    finally:
        # Restore original sys.argv
        sys.argv = original_argv


if __name__ == "__main__":
    test_bal_auto_date_range_detection()
    test_reg_auto_date_range_detection()
    test_bal_auto_date_range_with_account_filter()
    test_bal_auto_date_range_with_range_syntax()
    print("All end-to-end tests passed!")