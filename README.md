# ledger2bql
A Ledger CLI-like query syntax for Beancount

Implemented in Python.

The package is available at 
[![PyPI version](https://img.shields.io/pypi/v/ledger2bql.svg)](https://pypi.org/project/ledger2bql/).

# Introduction

BQL is quite a powerful language for slicing and dicing Beancount data. But, when all you need are simple queries, writing every field and filter seems tedious. In comparison, Ledger CLI's syntax is short and effective. A simple `l b bank` will list all bank accounts, assuming a well-organized account tree.

The purpose of this project, a simple CLI utility, is to accept a Ledger-like syntax, generate an appropriate BQL statement, and run it for you.

This is very convenient for quick lookups and everyday insights into your financial data.

For more background on Ledger's query syntax, see the [docs](https://ledger-cli.org/doc/ledger3.html).

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
All tests use the `.env` file in the `tests/` directory to locate the sample ledger file. Make sure this file is properly configured with the correct path to `sample_ledger.bean`.

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

For a list of available parameters, simply run
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

To show a hierarchical view with parent accounts showing aggregated balances, use the `--hierarchy` or `-H` flag:
```sh
# l b --hierarchy

Your BQL query is:
SELECT account, sum(position) GROUP BY account ORDER BY account ASC

+--------------------------+------------------------------------------------+
| Account                  |                                        Balance |
|--------------------------+------------------------------------------------|
| Assets                   | 3,000.00 CHF 1,839.65 EUR -25.00 BAM -7.00 USD |
| Assets:Bank              |                      3,000.00 CHF 1,859.65 EUR |
| Assets:Bank:Bank03581    |                                   3,000.00 CHF |
| Assets:Bank:Checking     |                                   1,359.65 EUR |
| Assets:Bank:Savings      |                                     500.00 EUR |
| Assets:Cash              |                -25.00 BAM -20.00 EUR -7.00 USD |
| Assets:Cash:BAM          |                                     -25.00 BAM |
| Assets:Cash:Pocket-Money |                                     -20.00 EUR |
| Assets:Cash:USD          |                                      -7.00 USD |
| Equity                   |                        -1,000.00 EUR 12.00 ABC |
| Equity:Opening-Balances  |                                  -1,000.00 EUR |
| Equity:Stocks            |                                      12.00 ABC |
| Expenses                 |                  145.00 EUR 25.00 BAM 7.00 USD |
| Expenses:Food            |                           100.00 EUR 25.00 BAM |
| Expenses:Sweets          |                                      20.00 EUR |
| Expenses:Transport       |                                       7.00 USD |
| Expenses:Transport:Bus   |                                      10.00 EUR |
| Expenses:Transport:Train |                                      15.00 EUR |
| Income                   |                    -3,000.00 CHF -1,000.00 EUR |
| Income:Other             |                                  -3,000.00 CHF |
| Income:Salary            |                                  -1,000.00 EUR |
+--------------------------+------------------------------------------------+
```

To collapse accounts to a specific depth level, use the `--depth` option:
```sh
# l b --depth 2

Your BQL query is:
SELECT account, sum(position) GROUP BY account ORDER BY account ASC

+-------------------------+---------------------------------+
| Account                 |                         Balance |
|-------------------------+---------------------------------|
| Assets:Bank             |       3,000.00 CHF 1,859.65 EUR |
| Assets:Cash             | -25.00 BAM -20.00 EUR -7.00 USD |
| Equity:Opening-Balances |                   -1,000.00 EUR |
| Equity:Stocks           |                       12.00 ABC |
| Expenses:Food           |            100.00 EUR 25.00 BAM |
| Expenses:Sweets         |                       20.00 EUR |
| Expenses:Transport      |              7.00 USD 25.00 EUR |
| Income:Other            |                   -3,000.00 CHF |
| Income:Salary           |                   -1,000.00 EUR |
+-------------------------+---------------------------------+
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

# Automatic Paging

By default, ledger2bql uses your system's pager (like `less` on Unix systems or `more` on Windows) to display output. This is especially useful when viewing large reports with many transactions.

To disable automatic paging and display all output directly in the terminal, use the `--no-pager` flag:

```sh
l b --no-pager
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

### Excluding Accounts with "not"

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

### Advanced Account Filtering

You can use special syntax to match accounts more precisely:

- `^pattern` - Matches accounts that **start with** the specified pattern
  ```sh
  l b ^Assets:Bank
  ```
  This will show all accounts that start with "Assets:Bank", such as "Assets:Bank:Checking" and "Assets:Bank:Savings".

- `pattern$` - Matches accounts that **end with** the specified pattern
  ```sh
  l b Checking$
  ```
  This will show all accounts that end with "Checking", regardless of what comes before it.

- `^pattern$` - Matches accounts that **exactly match** the specified pattern
  ```sh
  l b ^Assets:Bank:Checking$
  ```
  This will show only the exact account "Assets:Bank:Checking", excluding any other accounts.

These patterns can be combined with the `not` keyword for exclusion filtering as well.

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

## Exchange

Converting all amounts to a specified currency is done via the `-X` or `--exchange` parameter. This works similarly to Ledger CLI's `-X` option, converting all transaction amounts and running totals to the target currency using Beancount's price database.

The currency code is case-insensitive and will be automatically converted to uppercase. When a conversion rate is not available for a particular currency pair, the converted amount will show as 0 in the target currency.

```sh
# Convert all amounts to USD
D:\src\ledger2bql>l r -X USD

Your BQL query is:
SELECT date, account, payee, narration, position, convert(position, 'USD') as converted_position

+------------+--------------------------+----------------+------------------+---------------+----------------+
| Date       | Account                  | Payee          | Narration        |        Amount |   Amount (USD) |
|------------+--------------------------+----------------+------------------+---------------+----------------|
| 2025-01-01 | Assets:Bank:Checking     |                | Initial Balance  |  1,000.00 EUR |   1,132.50 USD |
| 2025-01-01 | Equity:Opening-Balances  |                | Initial Balance  | -1,000.00 EUR |  -1,132.50 USD |
| 2025-05-01 | Expenses:Food            | Supermarket    | drinks           |     25.00 BAM |      25.00 BAM |  # No conversion rate available
| 2025-06-04 | Expenses:Transport       | Metro          | public transport |      7.00 USD |       7.00 USD |
+------------+--------------------------+----------------+------------------+---------------+----------------+

# Convert amounts and show running totals in both original and target currencies
D:\src\ledger2bql>l r -X usd -T  # lowercase currency is automatically converted to uppercase

Your BQL query is:
SELECT date, account, payee, narration, position, convert(position, 'USD') as converted_position

+------------+--------------------------+----------------+------------------+---------------+----------------+-----------------+---------------+
| Date       | Account                  | Payee          | Narration        |        Amount |   Amount (USD) |   Running Total |   Total (USD) |
|------------+--------------------------+----------------+------------------+---------------+----------------+-----------------+---------------|
| 2025-01-01 | Assets:Bank:Checking     |                | Initial Balance  |  1,000.00 EUR |   1,132.50 USD |    1,000.00 EUR |  1,132.50 USD |
| 2025-01-01 | Equity:Opening-Balances  |                | Initial Balance  | -1,000.00 EUR |  -1,132.50 USD |        0.00 EUR |      0.00 USD |
| 2025-05-01 | Expenses:Food            | Supermarket    | drinks           |     25.00 BAM |      25.00 BAM |       25.00 BAM |      0.00 USD |  # BAM not converted, USD total unchanged
| 2025-06-04 | Expenses:Transport       | Metro          | public transport |      7.00 USD |       7.00 USD |        7.00 USD |      7.00 USD |  # USD transaction updates USD total
+------------+--------------------------+----------------+------------------+---------------+----------------+-----------------+---------------+
```

For balance reports, the converted totals are shown in the "Total (USD)" column:

```sh
D:\src\ledger2bql>l b -X usd

Your BQL query is:
SELECT account, units(sum(position)) as Balance, convert(sum(position), 'USD') as Converted ORDER BY account ASC

+--------------------------+----------------------+---------------+
| Account                  |              Balance |   Total (USD) |
|--------------------------+----------------------+---------------|
| Assets:Bank:Checking     |         1,884.65 EUR |  2,134.37 USD |
| Assets:Cash:BAM          |           -25.00 BAM |      0.00 USD |
| Assets:Cash:Pocket-Money |           -20.00 EUR |    -22.65 USD |
| Assets:Cash:USD          |            -7.00 USD |     -7.00 USD |
| Equity:Opening-Balances  |        -1,000.00 EUR | -1,132.50 USD |
| Equity:Stocks            |            12.00 ABC |      0.00 USD |
| Expenses:Food            | 100.00 EUR 25.00 BAM |    113.25 USD |
| Expenses:Sweets          |            20.00 EUR |     22.65 USD |
| Expenses:Transport       |             7.00 USD |      7.00 USD |
| Income:Salary            |        -1,000.00 EUR | -1,132.50 USD |
+--------------------------+----------------------+---------------+
```

# License

See the [license](LICENSE) file.