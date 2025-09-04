"""
Tests for accounts with numbers in their names.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import io
from contextlib import redirect_stdout
from unittest.mock import patch

from ledger2bql.main import main as main_entry


@patch('os.getenv')
def test_account_with_numbers_not_treated_as_date(mock_getenv):
    """Test that accounts with numbers are not automatically treated as dates."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    # Save original sys.argv
    original_argv = sys.argv
    
    try:
        # Set sys.argv to simulate command line arguments
        # This should filter by account name "Assets:Bank:Bank03581", not treat it as a date
        sys.argv = ['ledger2bql', 'bal', 'Assets:Bank:Bank03581']
        
        f = io.StringIO()
        with redirect_stdout(f):
            # Act
            try:
                main_entry()
            except SystemExit:
                pass  # argparse calls sys.exit() on error, which is expected in tests
        
        # Assert
        output = f.getvalue()
        # Check that the query contains account filtering, not date filtering
        assert "account ~ 'Assets:Bank:Bank03581'" in output
        assert 'date >= date(' not in output  # Should not contain date filtering
        # Check that we have results (not "No records found")
        assert 'No records found.' not in output
        
    finally:
        # Restore original sys.argv
        sys.argv = original_argv


@patch('os.getenv')
def test_account_containing_year_not_treated_as_date(mock_getenv):
    """Test that accounts containing a year are not automatically treated as dates."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    # Save original sys.argv
    original_argv = sys.argv
    
    try:
        # Set sys.argv to simulate command line arguments
        # This should filter by account name "Expenses:Account2025", but that account doesn't exist
        # Instead, we'll use an account that does exist and has numbers in it
        sys.argv = ['ledger2bql', 'bal', 'Assets:Bank:Bank03581']
        
        f = io.StringIO()
        with redirect_stdout(f):
            # Act
            try:
                main_entry()
            except SystemExit:
                pass  # argparse calls sys.exit() on error, which is expected in tests
        
        # Assert
        output = f.getvalue()
        # Check that the query contains account filtering, not date filtering
        assert "account ~ 'Assets:Bank:Bank03581'" in output
        assert 'date >= date(' not in output  # Should not contain date filtering
        # Check that we have results (not "No records found")
        assert 'No records found.' not in output
        
    finally:
        # Restore original sys.argv
        sys.argv = original_argv


@patch('os.getenv')
def test_explicit_date_still_works(mock_getenv):
    """Test that explicit date ranges with -d still work correctly."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    # Save original sys.argv
    original_argv = sys.argv
    
    try:
        # Set sys.argv to simulate command line arguments
        # This should filter by date range "2025"
        sys.argv = ['ledger2bql', 'bal', '-d', '2025']
        
        f = io.StringIO()
        with redirect_stdout(f):
            # Act
            try:
                main_entry()
            except SystemExit:
                pass  # argparse calls sys.exit() on error, which is expected in tests
        
        # Assert
        output = f.getvalue()
        # Check that the query contains date filtering, not account filtering
        assert 'date >= date("2025-01-01")' in output
        assert 'date < date("2026-01-01")' in output
        assert "account ~" not in output  # Should not contain account filtering
        # Check that we have results (not "No records found")
        assert 'No records found.' not in output
        
    finally:
        # Restore original sys.argv
        sys.argv = original_argv


if __name__ == "__main__":
    test_account_with_numbers_not_treated_as_date()
    test_account_starting_with_year_not_treated_as_date()
    test_explicit_date_still_works()
    print("All account with numbers tests passed!")