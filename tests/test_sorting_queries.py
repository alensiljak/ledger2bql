"""
Test to verify that the register command doesn't apply default sorting in the BQL query.
"""

from tests.test_utils import run_reg_command


def test_register_no_default_sort_query():
    """Test that register command doesn't include ORDER BY in the BQL query by default."""
    # Run the register command without explicit sort
    result = run_reg_command()

    # Verify the command executed successfully
    assert result.exit_code == 0

    # Check that the BQL query doesn't contain ORDER BY (no default sorting)
    assert "Your BQL query is:" in result.output
    assert "ORDER BY" not in result.output


def test_register_explicit_sort_query():
    """Test that register command includes ORDER BY in the BQL query when explicitly requested with non-default field."""
    # Run the register command with explicit sort by date (non-default field)
    result = run_reg_command(["-S", "date"])

    # Verify the command executed successfully
    assert result.exit_code == 0

    # Check that the BQL query contains ORDER BY (explicit sorting)
    assert "Your BQL query is:" in result.output
    assert "ORDER BY date" in result.output


def test_register_explicit_account_sort_ignored():
    """Test that register command ignores explicit sort by 'account' (the default)."""
    # Run the register command with explicit sort by account (the default)
    result = run_reg_command(["-S", "account"])

    # Verify the command executed successfully
    assert result.exit_code == 0

    # Check that the BQL query doesn't contain ORDER BY (default sorting ignored)
    assert "Your BQL query is:" in result.output
    assert "ORDER BY" not in result.output


def test_balance_default_sort_query():
    """Test that balance command includes ORDER BY in the BQL query by default."""
    from tests.test_utils import run_bal_command

    # Run the balance command without explicit sort
    result = run_bal_command()

    # Verify the command executed successfully
    assert result.exit_code == 0

    # Check that the BQL query contains ORDER BY (default sorting)
    assert "Your BQL query is:" in result.output
    assert "ORDER BY" in result.output
