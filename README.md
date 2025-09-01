# ledger2bql
Translate Ledger CLI query syntax into BQL

Implemented in Python.

The package is available at https://pypi.org/project/ledger2bql/.

# Introduction

BQL is quite a powerful language for slicing and dicing Beancount data. But, when all you need are simple queries, writing every field and filter seems tedios. In comparison, Ledger CLI's syntax is short and efficient. A simple `l b bank` will list all bank accounts, assuming a well-organized account tree.

The purpose of this project, a simple CLI utility, is to accept a Ledger-like syntax, generate an appropriate BQL statement, and run it for you.

# Development

## Setup
Clone the repository.
Add an `.env` file, specifying the `BEANCOUNT_FILE` location.
```
BEANCOUNT_FILE=tests/sample_ledger.bean
```

```sh
uv sync
```

## Build
```sh
uv build
```

## Run
```sh
uv run ledger2bql
```
or run
```sh
l ...
```
# Usage

Install the package:
```sh
uv pip install ledger2bql
# or
uv tool install ledger2bql
```

Set the `BEANCOUNT_FILE` variable to point to your Beancount ledger file.
You can create an .env file, to customize different ledgers for different folders.

Run
```sh
ledger2bql b card
ledger2bql r card -b 2025-08-01
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

## Register
Command 
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