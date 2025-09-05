"""
Test for Unicode character handling in account names and payees.
"""
import os
from dotenv import load_dotenv

from tests.test_utils import run_reg_command


# Load environment variables from the tests directory
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path, override=True)


def test_ss_display():
    """Test that ß is displayed correctly"""
    # Act
    result = run_reg_command(['@priel'])

    # Assert
    assert result.exit_code == 0
    output = result.output

    # Make sure that ss is output correctly.
    assert "Großer" in output


def test_ch_display():
    """Test that ć is displayed correctly"""
    # Act
    result = run_reg_command(['-d', '2025-05-01'])

    # Assert
    assert result.exit_code == 0
    output = result.output

    # Make sure that ss is output correctly.
    assert "piće" in output
