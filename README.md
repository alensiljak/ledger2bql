# ledger2bql
A Ledger CLI-like query syntax for Beancount

Implemented in Python.

The package is available at 
[![PyPI version](https://img.shields.io/pypi/v/ledger2bql.svg)](https://pypi.org/project/ledger2bql/).

# Introduction

BQL is quite a powerful language for slicing and dicing Beancount data. But, when all you need are simple queries, writing every field and filter seems tedious. In comparison, Ledger CLI's syntax is short and effective. A simple `l b bank` will list all bank accounts, assuming a well-organized account tree.

The purpose of this project, a simple CLI utility, is to accept a Ledger-like syntax, generate an appropriate BQL statement, and run it for you.

This is very convenient for quick lookups and everyday insights into your financial data.

# Development

Clone the repository.
Add an `.env` file, specifying the `BEANCOUNT_FILE` location.
```
BEANCOUNT_FILE=tests/sample_ledger.bean
```
Install the dependencies.
```sh
uv sync
```

Build
```sh
uv build
```

Run
```sh
uv run ledger2bql
```
or run
```sh
l ...
```

## Tests
Since the app is using `.env` file for environment variables, make sure that `BEANCOUNT_FILE` is set to the `sample_ledger.bean` in the `tests/` directory.

# Usage

Install the package:
```sh
uv pip install ledger2bql
# or
uv tool install ledger2bql
```

Set the `BEANCOUNT_FILE` variable to point to your Beancount ledger file.
You can create an .env file, to customize different ledgers for different folders.

For convenience, you can use a `l.cmd` as a shortcut for ledger2bql. See the actual file in the project root.

Run
```sh
ledger2bql b card
ledger2bql r card -b 2025-08
```

To get the list of available parameters, simply run
```sh
ledger2bql
ledger2bql bal --help
ledger2bql reg --help
```

# Output

## Balance

Running
```sh
l b
```
will output
```
Your BQL query is:
SELECT account, sum(position) GROUP BY account ORDER BY account ASC

+--------------------------+---------------+
| Account                  |       Balance |
|--------------------------+---------------|
| Assets:Bank:Checking     |  1,900.00 EUR |
| Assets:Cash:Pocket-Money |    -20.00 EUR |
| Equity:Opening-Balances  | -1,000.00 EUR |
| Expenses:Food            |    100.00 EUR |
| Expenses:Sweets          |     20.00 EUR |
| Income:Salary            | -1,000.00 EUR |
+--------------------------+---------------+
```

To show a grand total row at the end of the balance report, use the `--total` or `-T` flag:
```sh
# l b --total

Your BQL query is:
SELECT account, sum(position) GROUP BY account ORDER BY account ASC

+--------------------------+---------------+
| Account                  |       Balance |
|--------------------------+---------------|
| Assets:Bank:Checking     |  1,900.00 EUR |
| Assets:Cash:Pocket-Money |    -20.00 EUR |
| Equity:Opening-Balances  | -1,000.00 EUR |
| Expenses:Food            |    100.00 EUR |
| Expenses:Sweets          |     20.00 EUR |
| Income:Salary            | -1,000.00 EUR |
|--------------------------+---------------|
| Total                    |    -15.35 EUR |
+--------------------------+---------------+
```

## Register

The register command lists transactions/postings. 
Running
```sh
l r
```
will output
```
Your BQL query is:
SELECT date, account, payee, narration, position

+------------+-------------------------+----------------+-------------+---------------+
| Date       | Account                 | Payee          | Narration   |        Amount |
|------------+-------------------------+----------------+-------------+---------------|
| 2025-01-01 | Assets:Bank:Checking    |                | Initial Bal |  1,000.00 EUR |
| 2025-01-01 | Equity:Opening-Balances |                | Initial Bal | -1,000.00 EUR |
| 2025-02-01 | Expenses:Sweets         | Ice Cream Shop | Ice Cream   |     20.00 EUR |
| 2025-02-01 | Assets:Cash:Pocket-Mone | Ice Cream Shop | Ice Cream   |    -20.00 EUR |
| 2025-03-01 | Expenses:Food           | Grocery Store  | Groceries   |    100.00 EUR |
| 2025-03-01 | Assets:Bank:Checking    | Grocery Store  | Groceries   |   -100.00 EUR |
+------------+-------------------------+----------------+-------------+---------------+
```

To show a running total column in the register report, use the `--total` or `-T` flag:
```sh
# l r --total

Your BQL query is:
SELECT date, account, payee, narration, position

+------------+--------------------------+----------------+------------------+---------------+-----------------+
| Date       | Account                  | Payee          | Narration        |        Amount |   Running Total |
|------------+--------------------------+----------------+------------------+---------------+-----------------|
| 2025-01-01 | Assets:Bank:Checking     |                | Initial Balance  |  1,000.00 EUR |    1,000.00 EUR |
| 2025-01-01 | Equity:Opening-Balances  |                | Initial Balance  | -1,000.00 EUR |        0.00 EUR |
| 2025-02-01 | Expenses:Sweets          | Ice Cream Shop | Ice Cream        |     20.00 EUR |       20.00 EUR |
| 2025-02-01 | Assets:Cash:Pocket-Money | Ice Cream Shop | Ice Cream        |    -20.00 EUR |        0.00 EUR |
| 2025-03-01 | Expenses:Food            | Grocery Store  | Groceries        |    100.00 EUR |      100.00 EUR |
| 2025-03-01 | Assets:Bank:Checking     | Grocery Store  | Groceries        |   -100.00 EUR |        0.00 EUR |
+------------+--------------------------+----------------+------------------+---------------+-----------------+
```

# Filter Syntax

The filters have initially matched the Ledger CLI syntax but some have been adjusted for convenience.

They can be combined, providing powerful filtering capabilities. I.e.
to list all transactions in BAM, in the specified date period, for accounts containing "exp", to a payee/narration containing "super":
```sh
l r -c bam -d 2025-01-05..2025-01-17 exp @super
```

## Account

To narrow-down to certain accounts only, simply write a part of the account name.
```sh
l r exp
```
outputs
```
Your BQL query is:
SELECT date, account, payee, narration, position WHERE account ~ 'exp' ORDER BY date, account

+------------+-----------------+----------------+-------------+------------+
| Date       | Account         | Payee          | Narration   |     Amount |
|------------+-----------------+----------------+-------------+------------|
| 2025-02-01 | Expenses:Sweets | Ice Cream Shop | Ice Cream   |  20.00 EUR |
| 2025-03-01 | Expenses:Food   | Grocery Store  | Groceries   | 100.00 EUR |
+------------+-----------------+----------------+-------------+------------+
```

## Excluding Accounts with "not"

To exclude certain accounts from the results, use the `not` keyword followed by account patterns:
```sh
l b not bank
```
This will show all accounts except those matching "bank". You can also exclude multiple patterns:
```sh
l r not bank cash
```
This will show all transactions except those involving bank or cash accounts.

You can combine inclusion and exclusion filters:
```sh
l b assets not bank
```
This will show only asset accounts that don't match "bank".

## Amount

Filtering by amount is done via the `-a` or `--amount` parameter. This allows you to filter transactions based on their amount values.

The amount filter supports the following operators:
- `>` - Greater than
- `<` - Less than
- `>=` - Greater than or equal to
- `<=` - Less than or equal to
- `=` - Equal to (default if no operator is specified)

You can also specify a currency code after the amount to filter by both amount and currency.

```sh
# Show transactions with amounts greater than 50 (in any currency)
l r -a ">50"

# Show transactions with amounts greater than 50 EUR
l r -a ">50EUR"

# Show transactions with amounts less than or equal to 100
l r -a "<=100"

# Show transactions with amounts equal to 25 BAM
l r -a "=25BAM"
l r -a "25BAM"  # equivalent to above (default is =)
```

Note: The amount filter values must be quoted to prevent shell interpretation of the operators.

## Description / Payee

Similar to Ledger's Payee spec, `@some_store`, the `@` syntax is available. For Beancount, however, it is more useful to search through the Description, which is a combination of Payee and Narration fields.

```sh
D:\src\ledger2bql>l b @ice

Your BQL query is:
SELECT account, units(sum(position)) as Balance WHERE description ~ 'ice' ORDER BY account ASC

+--------------------------+------------+
| Account                  |    Balance |
|--------------------------+------------|
| Assets:Cash:Pocket-Money | -20.00 EUR |
| Expenses:Sweets          |  20.00 EUR |
+--------------------------+------------+
```

## Date Range

A new, date range, syntax has been introduced. Instead of using `-b 2025 -e 2025-06`, you can simply write `-d 2025..2025-06`.

```sh
D:\src\ledger2bql>l r -d 2025-01

Your BQL query is:
SELECT date, account, payee, narration, position WHERE date >= date("2025-01-01") AND date < date("2025-02-01")

+------------+-------------------------+---------+-----------------+---------------+
| Date       | Account                 | Payee   | Narration       |        Amount |
|------------+-------------------------+---------+-----------------+---------------|
| 2025-01-01 | Assets:Bank:Checking    |         | Initial Balance |  1,000.00 EUR |
| 2025-01-01 | Equity:Opening-Balances |         | Initial Balance | -1,000.00 EUR |
+------------+-------------------------+---------+-----------------+---------------+
```
The date range can be used either with both or with just a beginning/ending value.
Specifying just a value, without the `..` operator, will use it as a range, as well.

```sh
l b -d 2025-01-07..2025-02-15
l r -d 2025-03..
l r -d ..2025-03
l r -d 2025-03-01 # => 2025-03-01..2025-03-02
l r -d 2025-02    # => 2025-02-01..2025-03-01
l r -d 2025       # => 2025-01-01..2026-01-01
```

### Automatic Date Range Detection

As a convenience feature, you can now omit the `-d` flag when specifying date ranges. Any argument that starts with a 4-digit year (like `2025`) will be automatically treated as a date range.

```sh
# These are equivalent:
l b -d 2025
l b 2025

# These are also equivalent:
l r -d 2025-03
l r 2025-03

# Range syntax also works:
l b -d 2025..2026
l b 2025..2026
```

Since Beancount account names cannot start with numbers, there is no ambiguity when automatically detecting date ranges.

## Currency

Filtering by currency is done via `-c` parameter. The currency spec is case-insensitive. Multiple currencies can be specified, separated by comma, without spaces.

```sh
D:\src\ledger2bql>l r -c abc,bam

Your BQL query is:
SELECT date, account, payee, narration, position WHERE currency IN ('ABC', 'BAM')

+------------+-----------------+-------------+-----------------+------------+
| Date       | Account         | Payee       | Narration       |     Amount |
|------------+-----------------+-------------+-----------------+------------|
| 2025-04-01 | Equity:Stocks   |             | Buy Stocks      |   5.00 ABC |
| 2025-04-02 | Equity:Stocks   |             | Buy more stocks |   7.00 ABC |
| 2025-05-01 | Expenses:Food   | Supermarket | drinks          |  25.00 BAM |
| 2025-05-01 | Assets:Cash:BAM | Supermarket | drinks          | -25.00 BAM |
+------------+-----------------+-------------+-----------------+------------+
```

# License
See [[LICENSE]].
