"""Tests for transaction calculations and formatting."""

import pytest

from budget_tracker import (
    add_transaction,
    calculate_balance,
    check_budget_alert,
    format_currency,
    format_transaction,
    search_transactions,
    total_by_category,
)


def test_add_transaction_appends_and_returns_it():
    transactions = []
    result = add_transaction(transactions, "Coffee", 45.5, "food", "expense")
    assert transactions == [result]
    assert result["description"] == "Coffee"
    assert result["amount"] == 45.5
    assert result["category"] == "Food"
    assert result["type"] == "expense"


def test_add_transaction_rejects_invalid_type():
    with pytest.raises(ValueError):
        add_transaction([], "Salary", 20000, "work", "deposit")


def test_add_transaction_rejects_non_positive_amount():
    with pytest.raises(ValueError):
        add_transaction([], "Refund", 0, "shopping", "income")
    with pytest.raises(ValueError):
        add_transaction([], "Refund", -10, "shopping", "income")


def test_add_transaction_strips_and_rounds():
    transactions = []
    result = add_transaction(
        transactions, "  Uber ride  ", 33.999, "transport", "expense"
    )
    assert result["description"] == "Uber ride"
    assert result["amount"] == 34.0


def test_calculate_balance_mixed_transactions():
    transactions = [
        {
            "description": "Salary",
            "amount": 20000,
            "category": "Work",
            "type": "income",
        },
        {
            "description": "Rent",
            "amount": 6000,
            "category": "Housing",
            "type": "expense",
        },
        {
            "description": "Groceries",
            "amount": 1500,
            "category": "Food",
            "type": "expense",
        },
    ]
    assert calculate_balance(transactions) == 12500.0


def test_calculate_balance_empty_list_is_zero():
    assert calculate_balance([]) == 0.0


def test_calculate_balance_income_only():
    transactions = [
        {"description": "Gift", "amount": 500, "category": "Other", "type": "income"}
    ]
    assert calculate_balance(transactions) == 500.0


def test_total_by_category_aggregates_expenses_only_by_default():
    transactions = [
        {
            "description": "Salary",
            "amount": 20000,
            "category": "Work",
            "type": "income",
        },
        {"description": "Lunch", "amount": 80, "category": "Food", "type": "expense"},
        {"description": "Dinner", "amount": 120, "category": "Food", "type": "expense"},
        {
            "description": "Bus fare",
            "amount": 25,
            "category": "Transport",
            "type": "expense",
        },
    ]
    totals = total_by_category(transactions)
    assert totals == {"Food": 200, "Transport": 25}
    assert "Work" not in totals


def test_total_by_category_empty_list_returns_empty_dict():
    assert total_by_category([]) == {}


def test_total_by_category_can_filter_income_instead():
    transactions = [
        {
            "description": "Salary",
            "amount": 20000,
            "category": "Work",
            "type": "income",
        },
        {"description": "Lunch", "amount": 80, "category": "Food", "type": "expense"},
    ]
    assert total_by_category(transactions, type_filter="income") == {"Work": 20000}


def test_search_transactions_matches_substring_case_insensitively():
    transactions = [
        {
            "description": "Uber ride",
            "amount": 60,
            "category": "Transport",
            "type": "expense",
        },
        {
            "description": "Uber Eats",
            "amount": 150,
            "category": "Food",
            "type": "expense",
        },
        {
            "description": "Rent",
            "amount": 6000,
            "category": "Housing",
            "type": "expense",
        },
    ]
    results = search_transactions(transactions, "uber")
    assert len(results) == 2


def test_search_transactions_no_match_returns_empty_list():
    transactions = [
        {
            "description": "Rent",
            "amount": 6000,
            "category": "Housing",
            "type": "expense",
        }
    ]
    assert search_transactions(transactions, "groceries") == []


def test_check_budget_alert_flags_categories_over_limit():
    spent = {"Food": 1200, "Transport": 300}
    limits = {"Food": 1000, "Transport": 500}
    alerts = check_budget_alert(spent, limits)
    assert len(alerts) == 1
    assert "Food" in alerts[0]
    assert "200.00" in alerts[0]


def test_check_budget_alert_exactly_at_limit_is_not_an_alert():
    spent = {"Food": 1000}
    limits = {"Food": 1000}
    assert check_budget_alert(spent, limits) == []


def test_check_budget_alert_ignores_categories_with_no_configured_limit():
    spent = {"Entertainment": 5000}
    limits = {}
    assert check_budget_alert(spent, limits) == []


def test_format_currency():
    assert format_currency(1234.5) == "R1,234.50"
    assert format_currency(0) == "R0.00"


def test_format_transaction_shows_sign_and_category():
    transaction = {
        "description": "Coffee",
        "amount": 45.5,
        "category": "Food",
        "type": "expense",
    }
    line = format_transaction(transaction)
    assert "-" in line
    assert "Food" in line
    assert "Coffee" in line
