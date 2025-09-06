"""
Tests for "starts with" (^) and "ends with" ($) account name filtering syntax.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import io
from contextlib import redirect_stdout

from ledger2bql.main import main as main_entry


def test_starts_with_syntax():
    """Test the ^ (starts with) syntax for account filtering."""

    # Save original sys.argv
    original_argv = sys.argv

    try:
        # Set sys.argv to simulate command line arguments
        sys.argv = ["ledger2bql", "bal", "^Assets:Bank"]

        f = io.StringIO()
        with redirect_stdout(f):
            # Act
            try:
                main_entry()
            except SystemExit:
                pass  # argparse calls sys.exit() on error, which is expected in tests

        # Assert
        output = f.getvalue()
        # Check that the query uses ~ for starts with syntax
        assert "account ~ '^Assets:Bank'" in output
        # Check that we have results (not "No records found")
        assert "No records found." not in output

    finally:
        # Restore original sys.argv
        sys.argv = original_argv


def test_ends_with_syntax():
    """Test the $ (ends with) syntax for account filtering."""

    # Save original sys.argv
    original_argv = sys.argv

    try:
        # Set sys.argv to simulate command line arguments
        sys.argv = ["ledger2bql", "bal", "Checking$"]

        f = io.StringIO()
        with redirect_stdout(f):
            # Act
            try:
                main_entry()
            except SystemExit:
                pass  # argparse calls sys.exit() on error, which is expected in tests

        # Assert
        output = f.getvalue()
        # Check that the query uses ~ for ends with syntax
        assert "account ~ 'Checking$'" in output
        # Check that we have results (not "No records found")
        assert "No records found." not in output

    finally:
        # Restore original sys.argv
        sys.argv = original_argv


def test_exact_match_syntax():
    """Test the ^...$ (exact match) syntax for account filtering."""

    # Save original sys.argv
    original_argv = sys.argv

    try:
        # Set sys.argv to simulate command line arguments
        sys.argv = ["ledger2bql", "bal", "^Assets:Bank:Checking$"]

        f = io.StringIO()
        with redirect_stdout(f):
            # Act
            try:
                main_entry()
            except SystemExit:
                pass  # argparse calls sys.exit() on error, which is expected in tests

        # Assert
        output = f.getvalue()
        # Check that the query uses ~ for exact match syntax
        assert "account ~ '^Assets:Bank:Checking$'" in output
        # Check that we have results (not "No records found")
        assert "No records found." not in output

    finally:
        # Restore original sys.argv
        sys.argv = original_argv


def test_starts_with_exclusion():
    """Test the ^ (starts with) syntax for account exclusion."""

    # Save original sys.argv
    original_argv = sys.argv

    try:
        # Set sys.argv to simulate command line arguments
        sys.argv = ["ledger2bql", "bal", "Assets", "not", "^Expenses"]

        f = io.StringIO()
        with redirect_stdout(f):
            # Act
            try:
                main_entry()
            except SystemExit:
                pass  # argparse calls sys.exit() on error, which is expected in tests

        # Assert
        output = f.getvalue()
        # Check that the query uses NOT ~ for starts with exclusion syntax
        assert "NOT (account ~ '^Expenses')" in output
        # Check that we have results (not "No records found")
        assert "No records found." not in output

    finally:
        # Restore original sys.argv
        sys.argv = original_argv


def test_ends_with_exclusion():
    """Test the $ (ends with) syntax for account exclusion."""

    # Save original sys.argv
    original_argv = sys.argv

    try:
        # Set sys.argv to simulate command line arguments
        sys.argv = ["ledger2bql", "bal", "Assets", "not", "Checking$"]

        f = io.StringIO()
        with redirect_stdout(f):
            # Act
            try:
                main_entry()
            except SystemExit:
                pass  # argparse calls sys.exit() on error, which is expected in tests

        # Assert
        output = f.getvalue()
        # Check that the query uses NOT ~ for ends with exclusion syntax
        assert "NOT (account ~ 'Checking$')" in output
        # Check that we have results (not "No records found")
        assert "No records found." not in output

    finally:
        # Restore original sys.argv
        sys.argv = original_argv


if __name__ == "__main__":
    test_starts_with_syntax()
    test_ends_with_syntax()
    test_exact_match_syntax()
    test_starts_with_exclusion()
    test_ends_with_exclusion()
    print("All starts with / ends with tests passed!")
