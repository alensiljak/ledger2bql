"""
Tests for the exchange (-X) functionality.
"""
import io
import os
from contextlib import redirect_stdout
from unittest.mock import patch

from ledger2bql.ledger_bal_to_bql import main as bal_main
from ledger2bql.ledger_reg_to_bql import main as reg_main


@patch('os.getenv')
def test_bal_exchange_eur_to_usd(mock_getenv):
    """Test balance command with EUR to USD exchange."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', '--exchange', 'USD']):
            # Act
            bal_main()

    # Assert
    output = f.getvalue()
    
    # The query should use convert function
    assert "convert(sum(position), 'USD')" in output
    
    # Should show converted balances
    assert "Total (USD)" in output


@patch('os.getenv')
def test_reg_exchange_eur_to_usd(mock_getenv):
    """Test register command with EUR to USD exchange."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['reg', '--exchange', 'USD']):
            # Act
            reg_main()

    # Assert
    output = f.getvalue()
    
    # The query should use convert function
    assert "convert(position, 'USD')" in output
    
    # Should show converted amounts
    assert "Amount" in output


@patch('os.getenv')
def test_bal_exchange_with_total(mock_getenv):
    """Test balance command with exchange and total."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal', '--exchange', 'USD', '--total']):
            # Act
            bal_main()

    # Assert
    output = f.getvalue()
    
    # Should show converted balances and total
    assert "Total (USD)" in output
    assert "Total" in output


@patch('os.getenv')
def test_reg_exchange_with_total(mock_getenv):
    """Test register command with exchange and total."""
    # Arrange
    mock_getenv.return_value = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')
    )

    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['reg', '--exchange', 'USD', '--total']):
            # Act
            reg_main()

    # Assert
    output = f.getvalue()
    
    # Should show converted amounts and running totals
    assert "Running Total" in output