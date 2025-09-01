import pytest
from unittest.mock import patch
import io
from contextlib import redirect_stdout
import os

from ledger2bql.ledger_reg_to_bql import main as reg_main

@patch('os.getenv')
def test_reg_no_args(mock_getenv):
    # Arrange
    mock_getenv.return_value = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_ledger.bean'))
    
    f = io.StringIO()
    with redirect_stdout(f):
        with patch('sys.argv', ['reg']):
            # Act
            reg_main()
    
    # Assert
    output = f.getvalue()
    assert "2025-02-01" in output
    assert "Ice Cream Shop" in output
    assert "Ice Cream" in output
    assert "Expenses:Sweets" in output
    assert "20.00 EUR" in output
