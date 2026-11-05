"""Run the budget tracker's command-line menu."""

from budget_tracker import (
    VALID_TYPES,
    add_transaction,
    calculate_balance,
    check_budget_alert,
    format_currency,
    format_transaction,
    search_transactions,
    total_by_category,
    validate_amount,
)

MENU = """
--- Personal Budget Tracker ---
1. Add a transaction
2. View all transactions
3. View spending by category
4. View balance
5. Search transactions
6. Set a category budget limit
7. Exit
"""


def prompt_text(label):
    """Ask again if the user leaves a required field blank."""
    while True:
        text = input(f"{label}: ").strip()
        if text:
            return text
        print("This field cannot be blank.")


def prompt_amount(label):
    """Ask for a valid amount using the same rules as the transaction logic."""
    while True:
        try:
            return validate_amount(input(f"{label}: ").strip())
        except ValueError as error:
            print(error)


def show_budget_alerts(transactions, budget_limits, category):
    spent = total_by_category(transactions).get(category, 0)
    for alert in check_budget_alert({category: spent}, budget_limits):
        print(alert)


def handle_add_transaction(transactions, budget_limits):
    description = prompt_text("Description")
    amount = prompt_amount("Amount")

    while True:
        transaction_type = input("Type (income/expense): ").strip().lower()
        if transaction_type in VALID_TYPES:
            break
        print("Please type income or expense.")

    category = prompt_text("Category")
    transaction = add_transaction(
        transactions, description, amount, category, transaction_type
    )
    print("Added.")
    if transaction_type == "expense":
        show_budget_alerts(transactions, budget_limits, transaction["category"])


def handle_view_all(transactions):
    if not transactions:
        print("No transactions yet.")
        return
    for transaction in transactions:
        print(format_transaction(transaction))


def handle_view_by_category(transactions):
    totals = total_by_category(transactions)
    if not totals:
        print("No expenses logged yet.")
        return
    for category, total in totals.items():
        print(f"{category:<15} {format_currency(total)}")


def handle_view_balance(transactions):
    print(f"Balance: {format_currency(calculate_balance(transactions))}")


def handle_search(transactions):
    keyword = prompt_text("Search keyword")
    matches = search_transactions(transactions, keyword)
    if not matches:
        print(f"No transactions found matching '{keyword}'.")
        return
    for transaction in matches:
        print(format_transaction(transaction))


def handle_set_budget(transactions, budget_limits):
    category = prompt_text("Category to set a budget for").title()
    limit = prompt_amount("Session limit")
    budget_limits[category] = limit
    print(f"Session budget for {category} set to {format_currency(limit)}.")
    show_budget_alerts(transactions, budget_limits, category)


def main():
    transactions = []
    budget_limits = {}
    print("Transactions and limits are kept for this session only.")
    try:
        while True:
            print(MENU)
            choice = input("Choose an option: ").strip()
            if choice == "1":
                handle_add_transaction(transactions, budget_limits)
            elif choice == "2":
                handle_view_all(transactions)
            elif choice == "3":
                handle_view_by_category(transactions)
            elif choice == "4":
                handle_view_balance(transactions)
            elif choice == "5":
                handle_search(transactions)
            elif choice == "6":
                handle_set_budget(transactions, budget_limits)
            elif choice == "7":
                break
            else:
                print("Invalid option, please choose 1-7.")
    except (EOFError, KeyboardInterrupt):
        print()
    print("Goodbye!")


if __name__ == "__main__":
    main()
