'''
parser tests
'''

import sys
from ledger2bql.ledger_bal_to_bql import create_parser, parse_query

def test_default_sort():
    '''
    Test adding sort criteria by default, when not specified.
    The accounts should be listed alphabetically.
    '''
    #command = "l b"
    # Simulate command-line arguments
    sys.argv = ["", "b"]

    # parse arguments
    parser = create_parser()
    args = parser.parse_args()
    generated_bql = parse_query(args)

    # confirm the generated BQL contains "ORDER BY"
    assert "ORDER BY" in generated_bql
