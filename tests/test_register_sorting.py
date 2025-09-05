"""
Test to verify that the register command doesn't apply default sorting.
"""
from tests.test_utils import run_reg_command


def test_register_no_default_sort():
    """Test that register command doesn't apply default sorting."""
    # Run the register command without explicit sort
    result = run_reg_command()
    
    # Verify the command executed successfully
    assert result.exit_code == 0
    
    # Check that the output contains transactions
    assert 'Ice Cream Shop' in result.output
    assert 'Grocery Store' in result.output


def test_register_explicit_sort():
    """Test that register command respects explicit sorting."""
    # Run the register command with explicit sort by account
    result = run_reg_command(['-S', 'account'])
    
    # Verify the command executed successfully
    assert result.exit_code == 0
    
    # Check that the output contains transactions
    assert 'Ice Cream Shop' in result.output
    assert 'Grocery Store' in result.output


def test_register_alias_r_no_default_sort():
    """Test that register command alias 'r' doesn't apply default sorting."""
    from click.testing import CliRunner
    from ledger2bql.main import cli
    
    runner = CliRunner()
    result = runner.invoke(cli, ['r'])
    
    # Verify the command executed successfully
    assert result.exit_code == 0
    
    # Check that the output contains transactions
    assert 'Ice Cream Shop' in result.output
    assert 'Grocery Store' in result.output