"""
Tests for the date range functionality.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ledger2bql.date_parser import parse_date_range


def test_date_range_parsing():
    """Test the date range parsing functionality."""
    
    # Test single year - should include all of 2025 (Jan 1 to Dec 31)
    result = parse_date_range("2025")
    assert result == ("2025-01-01", "2026-01-01")
    
    # Test single month - should include all of August 2025
    result = parse_date_range("2025-08")
    assert result == ("2025-08-01", "2025-09-01")
    
    # Test single day - should include just that day
    result = parse_date_range("2025-08-15")
    assert result == ("2025-08-15", "2025-08-16")
    
    # Test year range - from 2025 to 2026 (exclusive)
    result = parse_date_range("2025..2026")
    assert result == ("2025-01-01", "2026-01-01")
    
    # Test from month onwards
    result = parse_date_range("2025-08..")
    assert result == ("2025-08-01", None)
    
    # Test up to month - should be up to the beginning of that month (exclusive)
    result = parse_date_range("..2025-09")
    assert result == (None, "2025-09-01")
    
    # Test month range
    result = parse_date_range("2025-08..2025-10")
    assert result == ("2025-08-01", "2025-10-01")
    
    # Test year to month range (the specific case mentioned)
    result = parse_date_range("2025..2025-02")
    assert result == ("2025-01-01", "2025-02-01")
    
    # Test year to month range
    result = parse_date_range("2025..2025-10")
    assert result == ("2025-01-01", "2025-10-01")