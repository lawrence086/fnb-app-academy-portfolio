# Budget tracker

I built this command-line app while learning Python through FNB App Academy.
It records income and expenses in rand, groups spending by category, and
shows when a category goes over its budget.

## Features

- Add income and expenses with a description, amount, and category.
- View transactions, category spending, and the overall balance.
- Search descriptions without worrying about capital letters.
- Set or change a category's session budget and check for overspending.

## Run

Requires Python 3.11 or newer. The app uses only the standard library.
From the repository folder:

```sh
python3 budget-tracker/src/main.py
```

Choose an option from the menu and follow the prompts. For example, adding
R1,000 income and a R45.50 food expense gives a balance of R954.50. A food
budget of R40 then shows an overspend of R5.50.

## What I learned

I used a list of dictionaries to store transactions and functions to calculate
balances, group spending, and search descriptions. Keeping these calculations
separate from the menu makes them easier to test.

Input validation needed more care than just checking for a positive number:
an amount can round to zero, and Python also accepts special values such as
infinity. The app checks these cases before storing a transaction.

## Limitations

Transactions and budgets are stored in memory and disappear when the app
closes. Budgets cover the current session; there is no monthly tracking.
Amounts use Python floats rounded to two decimal places, so this is a
learning project rather than an accounting tool.

## Development

From the repository folder, create a virtual environment and install the
development tools:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest
python -m ruff check .
python -m black --check budget-tracker
```

On Windows, use `python` in place of `python3` and activate the environment
with `.venv\Scripts\activate` in Command Prompt.
