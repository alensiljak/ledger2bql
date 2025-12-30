"""
Test cases for the assert command functionality.
"""

import os
import sys
from click.testing import CliRunner

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set up environment
os.environ['BEANCOUNT_FILE'] = os.path.join(os.path.dirname(__file__), 'sample_ledger.bean')

from ledger2bql.main import cli


def test_assert_basic():
    """Test basic assert command without any filters."""
    runner = CliRunner()
    result = runner.invoke(cli, ['assert'])
    
    assert result.exit_code == 0
    assert "Your BQL query is:" in result.output
    assert "SELECT date, account, amount FROM #balances" in result.output
    assert "Assets:Bank:Checking" in result.output
    assert "595.47 EUR" in result.output
    assert "Assets:Bank:Savings" in result.output
    assert "5,775.09 EUR" in result.output
    assert "Assets:Cash:Pocket-Money" in result.output
    assert "0.00 EUR" in result.output


def test_assert_account_filter():
    """Test assert command with account filtering."""
    runner = CliRunner()
    result = runner.invoke(cli, ['assert', 'Assets:Bank'])
    
    assert result.exit_code == 0
    assert "WHERE account ~ 'Assets:Bank'" in result.output
    assert "Assets:Bank:Checking" in result.output
    assert "Assets:Bank:Savings" in result.output
    assert "Assets:Cash:Pocket-Money" not in result.output


def test_assert_date_filter():
    """Test assert command with date filtering."""
    runner = CliRunner()
    result = runner.invoke(cli, ['assert', '--begin', '2025-11-01'])
    
    assert result.exit_code == 0
    assert 'date >= date("2025-11-01")' in result.output
    # Should show results from November (both 2025-11-07 and 2025-11-08)
    assert "2025-11-" in result.output


def test_assert_currency_filter():
    """Test assert command with currency filtering."""
    runner = CliRunner()
    result = runner.invoke(cli, ['assert', '--currency', 'EUR'])
    
    assert result.exit_code == 0
    assert "amount.currency = 'EUR'" in result.output
    assert "595.47 EUR" in result.output
    assert "5,775.09 EUR" in result.output


def test_assert_amount_filter():
    """Test assert command with amount filtering."""
    runner = CliRunner()
    result = runner.invoke(cli, ['assert', '--amount', '>500'])
    
    assert result.exit_code == 0
    assert "amount.number > 500" in result.output
    assert "Assets:Bank:Checking" in result.output
    assert "Assets:Bank:Savings" in result.output
    assert "Assets:Cash:Pocket-Money" not in result.output


def test_assert_combined_filters():
    """Test assert command with multiple filters combined."""
    runner = CliRunner()
    result = runner.invoke(cli, ['assert', 'Assets:Bank', '--amount', '>500', '--currency', 'EUR'])
    
    assert result.exit_code == 0
    assert "account ~ 'Assets:Bank'" in result.output
    assert "amount.number > 500" in result.output
    assert "amount.currency = 'EUR'" in result.output
    assert "Assets:Bank:Checking" in result.output
    assert "Assets:Bank:Savings" in result.output


def test_assert_not_keyword():
    """Test assert command with 'not' keyword to exclude accounts."""
    runner = CliRunner()
    result = runner.invoke(cli, ['assert', 'not', 'Assets:Cash'])
    
    assert result.exit_code == 0
    assert "NOT (account ~ 'Assets:Cash')" in result.output
    assert "Assets:Bank:Checking" in result.output
    assert "Assets:Bank:Savings" in result.output
    assert "Assets:Cash:Pocket-Money" not in result.output


def test_assert_sorting():
    """Test assert command with sorting."""
    runner = CliRunner()
    result = runner.invoke(cli, ['assert', '--sort', 'account'])
    
    assert result.exit_code == 0
    assert "ORDER BY account ASC" in result.output


def test_assert_limit():
    """Test assert command with limit."""
    runner = CliRunner()
    result = runner.invoke(cli, ['assert', '--limit', '2'])
    
    assert result.exit_code == 0
    assert "LIMIT 2" in result.output
    # Should only show 2 results (one for 2025-11-07 and one for 2025-11-08)
    assert result.output.count("2025-11-") == 2
    assert "Assets:Bank:Checking" in result.output
    assert "Assets:Bank:Savings" in result.output


if __name__ == "__main__":
    # Run all tests
    test_assert_basic()
    test_assert_account_filter()
    test_assert_date_filter()
    test_assert_currency_filter()
    test_assert_amount_filter()
    test_assert_combined_filters()
    test_assert_not_keyword()
    test_assert_sorting()
    test_assert_limit()
    
    print("All assert command tests passed!")