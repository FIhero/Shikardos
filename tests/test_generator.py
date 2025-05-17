from typing import Any, Dict, List, Optional

import pytest

from src.generator import (
    card_number_generator,
    filter_by_currency,
    transaction_descriptions,
)


# Фикстуры для тестов
@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    return [
        {"amount": 100, "currency": "USD", "description": "Payment 1"},
        {"amount": 200, "currency": "EUR", "description": "Payment 2"},
        {"amount": 300, "currency": "USD", "description": "Payment 3"},
    ]


@pytest.fixture
def empty_transactions() -> List[Dict[str, Any]]:
    return []


# Параметризованные тесты для filter_by_currency
@pytest.mark.parametrize(
    "currency, expected_count, expected_descriptions",
    [
        ("USD", 2, ["Payment 1", "Payment 3"]),
        ("EUR", 1, ["Payment 2"]),
        ("GBP", 0, []),
    ],
)
def test_filter_by_currency_normal(
    sample_transactions: List[Dict[str, Any]],
    currency: str,
    expected_count: int,
    expected_descriptions: List[str],
) -> None:
    """Тестирует фильтрацию по валюте с параметризацией"""
    result: List[Dict[str, Any]] = list(filter_by_currency(sample_transactions, currency))
    assert len(result) == expected_count
    assert [t["description"] for t in result] == expected_descriptions
    assert all(t["currency"] == currency for t in result)


def test_filter_by_currency_empty(empty_transactions: List[Dict[str, Any]]) -> None:
    """Тестирует фильтрацию с пустым списком"""
    result: List[Dict[str, Any]] = list(filter_by_currency(empty_transactions, "USD"))
    assert len(result) == 0


def test_filter_by_currency_missing_key(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тестирует обработку транзакций без ключа currency"""
    modified_transactions: List[Dict[str, Any]] = sample_transactions + [{"amount": 400}]  # type: ignore
    result: List[Dict[str, Any]] = list(filter_by_currency(modified_transactions, "USD"))
    assert len(result) == 2


# Параметризованные тесты для transaction_descriptions
@pytest.mark.parametrize(
    "transactions, expected_descriptions",
    [
        (
            [
                {"amount": 100, "description": "Payment 1"},
                {"amount": 200, "description": "Payment 2"},
            ],
            ["Payment 1", "Payment 2"],
        ),
        (
            [
                {"amount": 100, "description": "A"},
                {"amount": 200},
                {"amount": 300, "description": "B"},
            ],
            ["A", None, "B"],
        ),
        ([], []),
    ],
)
def test_transaction_descriptions_parametrized(
    transactions: List[Dict[str, Any]], expected_descriptions: List[Optional[str]]
) -> None:
    """Параметризованный тест для получения описаний транзакций"""
    result: List[Optional[str]] = list(transaction_descriptions(transactions))
    assert result == expected_descriptions


# Параметризованные тесты для card_number_generator
@pytest.mark.parametrize(
    "start, end, expected",
    [
        (1, 3, ["0000 0000 0000 0001", "0000 0000 0000 0002", "0000 0000 0000 0003"]),
        (
            9998,
            10001,
            [
                "0000 0000 0000 9998",
                "0000 0000 0000 9999",
                "0000 0000 0001 0000",
                "0000 0000 0001 0001",
            ],
        ),
        (1234567890123456, 1234567890123456, ["1234 5678 9012 3456"]),
    ],
)
def test_card_number_generator_parametrized(
    start: int, end: int, expected: List[str]
) -> None:
    """Параметризованный тест генерации номеров карт"""
    result: List[str] = list(card_number_generator(start, end))
    assert result == expected


def test_card_number_generator_edge_cases() -> None:
    """Тестирует крайние значения"""
    min_result: str = next(card_number_generator(1, 1))
    assert min_result == "0000 0000 0000 0001"

    max_result: str = next(card_number_generator(9999999999999999, 9999999999999999))
    assert max_result == "9999 9999 9999 9999"


if __name__ == "__main__":
    pytest.main()
