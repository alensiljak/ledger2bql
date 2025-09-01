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

## Example

Running
```sh
l b cash
```
will output
```
Your BQL query is:

SELECT account, sum(position) as balance WHERE account ~ 'cash'

+--------------------------+------------+
| Account                  |    Balance |
|--------------------------+------------|
| Assets:Cash:Pocket-Money | -20.00 EUR |
+--------------------------+------------+
```