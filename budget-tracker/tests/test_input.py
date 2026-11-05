"""Check invalid input and the menu's main workflows."""

import pytest

from budget_tracker import add_transaction, validate_amount
from main import (
    handle_add_transaction,
    handle_set_budget,
    main,
    prompt_amount,
    prompt_text,
)


@pytest.mark.parametrize(
    "amount",
    ["nan", "inf", "-inf", "1e999", 0, -1, 0.001, "coffee", "", None, True],
)
def test_invalid_amount_does_not_add_a_transaction(amount):
    transactions = []
    with pytest.raises(ValueError):
        add_transaction(transactions, "Lunch", amount, "Food", "expense")
    assert transactions == []


@pytest.mark.parametrize(
    "amount, expected", [(0.01, 0.01), (33.999, 34.0), ("45.50", 45.5)]
)
def test_valid_amount_is_rounded_to_cents(amount, expected):
    assert validate_amount(amount) == expected


@pytest.mark.parametrize("description, category", [("", "Food"), ("Lunch", "  ")])
def test_blank_fields_do_not_add_a_transaction(description, category):
    transactions = []
    with pytest.raises(ValueError):
        add_transaction(transactions, description, 50, category, "expense")
    assert transactions == []


def enter_answers(monkeypatch, answers):
    answers = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))


def test_amount_prompt_retries_invalid_values(monkeypatch, capsys):
    enter_answers(monkeypatch, ["oops", "nan", "inf", "-1", "0.001", "45.50"])
    assert prompt_amount("Amount") == 45.5
    assert "at least R0.01" in capsys.readouterr().out


def test_text_prompt_retries_blank_values(monkeypatch, capsys):
    enter_answers(monkeypatch, ["", "  ", "  Lunch  "])
    assert prompt_text("Description") == "Lunch"
    assert capsys.readouterr().out.count("cannot be blank") == 2


@pytest.mark.parametrize("previous_limit", [None, 100])
def test_setting_or_lowering_budget_checks_existing_spending(
    monkeypatch, capsys, previous_limit
):
    transactions = []
    add_transaction(transactions, "Lunch", 60, "Food", "expense")
    limits = {} if previous_limit is None else {"Food": previous_limit}
    enter_answers(monkeypatch, [" food ", "50"])
    handle_set_budget(transactions, limits)
    assert limits == {"Food": 50}
    assert "over by R10.00" in capsys.readouterr().out


def test_adding_expense_only_reports_its_own_category(monkeypatch, capsys):
    transactions = []
    add_transaction(transactions, "Lunch", 60, "Food", "expense")
    enter_answers(
        monkeypatch, ["", "  Bus  ", "nan", "20", "wrong", "EXPENSE", "transport"]
    )
    handle_add_transaction(transactions, {"Food": 50, "Transport": 10})
    output = capsys.readouterr().out
    assert transactions[-1] == {
        "description": "Bus",
        "amount": 20,
        "category": "Transport",
        "type": "expense",
    }
    assert "Over budget in Transport" in output
    assert "Over budget in Food" not in output


def test_menu_workflow(monkeypatch, capsys):
    enter_answers(
        monkeypatch,
        [
            "wrong",
            "1",
            "Salary",
            "1000",
            "income",
            "Work",
            "1",
            "Lunch",
            "45.50",
            "expense",
            "Food",
            "2",
            "3",
            "4",
            "5",
            "lUnCh",
            "6",
            "food",
            "40",
            "7",
        ],
    )
    main()
    output = capsys.readouterr().out
    assert "Invalid option" in output
    assert "Balance: R954.50" in output
    assert "over by R5.50" in output
    assert output.count("Lunch") == 2
    assert output.endswith("Goodbye!\n")


@pytest.mark.parametrize("interruption", [EOFError, KeyboardInterrupt])
def test_menu_handles_interrupted_input(monkeypatch, capsys, interruption):
    def interrupt(prompt):
        raise interruption

    monkeypatch.setattr("builtins.input", interrupt)
    main()
    assert capsys.readouterr().out.endswith("Goodbye!\n")
