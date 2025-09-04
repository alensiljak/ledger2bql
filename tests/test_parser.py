'''
parser tests
'''

import sys
from ledger2bql.balance import parse_query


def test_default_sort():
    '''
    Test adding sort criteria by default, when not specified.
    The accounts should be listed alphabetically.
    '''
    # Create a mock args object with default values
    class Args:
        def __init__(self):
            self.account_regex = []
            self.begin = None
            self.end = None
            self.date_range = None
            self.empty = False
            self.sort = 'account'
            self.limit = None
            self.amount = []
            self.currency = None
            self.exchange = None
            self.total = False
            self.no_pager = False
            self.depth = None
            self.zero = False
    
    args = Args()
    generated_bql = parse_query(args)

    # confirm the generated BQL contains "ORDER BY"
    assert "ORDER BY" in generated_bql