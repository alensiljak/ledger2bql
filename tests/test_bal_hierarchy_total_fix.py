"""
Tests for the Balance command with hierarchy and total options combined.
Specifically tests the fix for double-counting issue.
"""

from tests.test_utils import run_bal_command, extract_table_data


def test_bal_with_hierarchy_and_total_no_double_counting():
    """Test that using --hierarchy and --total together doesn't double-count balances."""
    # Act
    result_hierarchical = run_bal_command(["--hierarchy", "--total"])
    result_regular = run_bal_command(["--total"])

    # Assert both commands succeeded
    assert result_hierarchical.exit_code == 0
    assert result_regular.exit_code == 0

    # Extract table data from both outputs
    table_lines_hierarchical = extract_table_data(
        result_hierarchical.output.splitlines()
    )
    table_lines_regular = extract_table_data(result_regular.output.splitlines())

    # Find the total rows in both outputs
    total_row_hierarchical = None
    total_row_regular = None

    for line in table_lines_hierarchical:
        if "| Total" in line:
            total_row_hierarchical = line
            break

    for line in table_lines_regular:
        if "| Total" in line:
            total_row_regular = line
            break

    # Assert that both total rows exist
    assert total_row_hierarchical is not None, (
        "Total row not found in hierarchical output"
    )
    assert total_row_regular is not None, "Total row not found in regular output"

    # Assert that the total values are the same (no double-counting)
    assert total_row_hierarchical == total_row_regular, (
        f"Total values don't match. Hierarchical: {total_row_hierarchical}, "
        f"Regular: {total_row_regular}. This indicates double-counting in hierarchical view."
    )
