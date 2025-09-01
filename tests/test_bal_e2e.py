'''
Tests for the Balance command.
'''
from unittest.mock import patch
import io
from contextlib import redirect_stdout
import os

from ledger2bql.ledger_bal_to_bql import main as bal_main

@patch('os.getenv')
def test_bal_no_args(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['bal']):
            # Act
            bal_main()
    
    # Assert
    output = f.getvalue()
    assert "Assets:Cash:Pocket-Money" in output
    assert "-20.00 EUR" in output
    assert "Expenses:Sweets" in output
    assert "20.00 EUR" in output
