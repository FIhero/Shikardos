from typing import Any, Optional

import pytest

from src.widget import get_date, mask_account_card


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("Visa Platinum 1234567812345678", "Visa Platinum 123456******5678"),
        ("МИР 1234567890123456", "МИР 123456******3456"),
        ("MasterCard 5555555555554444", "MasterCard 555555******4444"),
        ("Счет 12345678901234567890", "Счет ****************7890"),
        ("счет 98765432109876543210", "счет ****************3210"),
        ("JustTextWithoutNumber", "JustTextWithoutNumber"),
        ("", ""),
        ("CardTooShort 123", "CardTooShort 123"),
    ],
)
def test_mask_account_card_valid(input_str: str, expected: str) -> None:
    assert mask_account_card(input_str) == expected


@pytest.mark.parametrize(
    "iso_date, expected",
    [
        ("2023-12-31T00:00:00", "31.12.2023"),
        ("1999-01-01T12:34:56", "01.01.1999"),
        ("2000-02-29T00:00:00", "29.02.2000"),
        ("2023-13-01T00:00:00", None),
        ("2023-02-30T00:00:00", None),
        ("2023-04-31T00:00:00", None),
        ("", None),
        ("2023-12-31", None),
    ],
)
def test_get_date_valid(iso_date: str, expected: Optional[str]) -> None:
    assert get_date(iso_date) == expected


def test_error_handling(monkeypatch: Any) -> None:
    def mock_fail(_: str) -> str:
        raise ValueError("Test error")

    monkeypatch.setattr("src.widget.mask_account_card", mock_fail)
    assert mask_account_card("Счет 123") == "Счет 123"
    assert mask_account_card("Invalid !@# Data") == "Invalid !@# Data"


def test_get_date_empty_string() -> None:
    assert get_date("") is None
