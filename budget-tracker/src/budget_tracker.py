"""Transaction calculations and formatting for the budget tracker."""

from math import isfinite

VALID_TYPES = ("income", "expense")


def validate_amount(value):
    """Return a positive amount rounded to cents, or raise ValueError."""
    if isinstance(value, bool):
        raise ValueError("Please enter a number, e.g. 45.50.")
    try:
        amount = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("Please enter a number, e.g. 45.50.") from None
    if not isfinite(amount):
        raise ValueError("Please enter a finite amount.")
    amount = round(amount, 2)
    if amount <= 0:
        raise ValueError("Amount must be at least R0.01 after rounding.")
    return amount


def add_transaction(transactions, description, amount, category, transaction_type):
    """Validate and append a transaction, then return it."""
    if transaction_type not in VALID_TYPES:
        raise ValueError("Type must be income or expense.")
    description = description.strip()
    category = category.strip().title()
    if not description or not category:
        raise ValueError("Description and category cannot be blank.")
    transaction = {
        "description": description,
        "amount": validate_amount(amount),
        "category": category,
        "type": transaction_type,
    }
    transactions.append(transaction)
    return transaction


def calculate_balance(transactions):
    """Return total income minus expenses."""
    balance = 0.0
    for transaction in transactions:
        if transaction["type"] == "income":
            balance += transaction["amount"]
        else:
            balance -= transaction["amount"]
    return round(balance, 2)


def total_by_category(transactions, type_filter="expense"):
    """Group transaction amounts by category."""
    totals = {}
    for transaction in transactions:
        if transaction["type"] == type_filter:
            category = transaction["category"]
            totals[category] = round(totals.get(category, 0) + transaction["amount"], 2)
    return totals


def search_transactions(transactions, keyword):
    """Find descriptions containing the keyword, ignoring case."""
    keyword = keyword.strip().lower()
    matches = []
    for transaction in transactions:
        if keyword in transaction["description"].lower():
            matches.append(transaction)
    return matches


def check_budget_alert(spent_by_category, budget_limits):
    """Return a message for each category that exceeds its limit."""
    alerts = []
    for category, spent in spent_by_category.items():
        limit = budget_limits.get(category)
        if limit is not None and spent > limit:
            over_by = round(spent - limit, 2)
            alerts.append(
                f"Over budget in {category}: spent R{spent:.2f} "
                f"(limit R{limit:.2f}, over by R{over_by:.2f})"
            )
    return alerts


def format_currency(amount):
    """Format an amount in South African rand."""
    return f"R{amount:,.2f}"


def format_transaction(transaction):
    """Format a transaction as a ledger entry."""
    sign = "+" if transaction["type"] == "income" else "-"
    return (
        f"{sign}{format_currency(transaction['amount']):>10}  "
        f"[{transaction['category']:<12}] {transaction['description']}"
    )
