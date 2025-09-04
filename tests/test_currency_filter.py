#!/usr/bin/env python3
"""
Test script for the currency filter functionality.
"""
import os
import sys
import subprocess

# Add the src directory to the path so we can import ledger2bql
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_currency_filter():
    """Test the currency filter functionality."""
    # Use the BEANCOUNT_FILE environment variable from .env
    env = os.environ.copy()
    
    # Test 1: Run balance command with EUR currency filter
    print("Testing balance command with EUR currency filter...")
    result = subprocess.run([
        sys.executable, '-m', 'ledger2bql.main', 'bal', '--currency', 'EUR'
    ], capture_output=True, text=True, env=env)
    
    print("Exit code:", result.returncode)
    print("Stdout:", result.stdout)
    if result.stderr:
        print("Stderr:", result.stderr)
    
    # Test 2: Run register command with ABC currency filter
    print("\nTesting register command with ABC currency filter...")
    result = subprocess.run([
        sys.executable, '-m', 'ledger2bql.main', 'reg', '--currency', 'ABC'
    ], capture_output=True, text=True, env=env)
    
    print("Exit code:", result.returncode)
    print("Stdout:", result.stdout)
    if result.stderr:
        print("Stderr:", result.stderr)

if __name__ == '__main__':
    test_currency_filter()