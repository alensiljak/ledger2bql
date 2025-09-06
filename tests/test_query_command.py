import subprocess


def test_query_command():
    """Test the query command functionality."""
    # Test 1: Full command with exact name
    result = subprocess.run(
        ["uv", "run", "ledger2bql", "query", "holidays"],
        cwd=".",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Command failed with exit code {result.returncode}"
    assert "Your BQL query is:" in result.stdout
    assert "select * where payee ~ 'holiday'" in result.stdout
    assert "Holiday" in result.stdout
    print("Test 1 passed: Full command with exact name")

    # Test 2: Short alias with exact name
    result = subprocess.run(
        ["uv", "run", "ledger2bql", "q", "holidays"],
        cwd=".",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Command failed with exit code {result.returncode}"
    assert "Your BQL query is:" in result.stdout
    assert "select * where payee ~ 'holiday'" in result.stdout
    assert "Holiday" in result.stdout
    print("Test 2 passed: Short alias with exact name")

    # Test 3: Short alias with partial name
    result = subprocess.run(
        ["uv", "run", "ledger2bql", "q", "holi"],
        cwd=".",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Command failed with exit code {result.returncode}"
    assert "Your BQL query is:" in result.stdout
    assert "select * where payee ~ 'holiday'" in result.stdout
    assert "Holiday" in result.stdout
    print("Test 3 passed: Short alias with partial name")

    # Test 4: Non-existent query
    result = subprocess.run(
        ["uv", "run", "ledger2bql", "q", "nonexistent"],
        cwd=".",
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0, "Command should have failed but didn't"
    assert (
        "not found in the ledger file" in result.stderr
        or "not found in the ledger file" in result.stdout
    )
    print("Test 4 passed: Non-existent query correctly fails")

    print("All tests passed!")


if __name__ == "__main__":
    test_query_command()
