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


# Тесты для filter_by_currency
def test_filter_by_currency_normal(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тестирует фильтрацию по валюте в обычном случае"""
    result: List[Dict[str, Any]] = list(filter_by_currency(sample_transactions, "USD"))
    assert len(result) == 2
    assert all(t["currency"] == "USD" for t in result)


def test_filter_by_currency_empty(empty_transactions: List[Dict[str, Any]]) -> None:
    """Тестирует фильтрацию с пустым списком"""
    result: List[Dict[str, Any]] = list(filter_by_currency(empty_transactions, "USD"))
    assert len(result) == 0


def test_filter_by_currency_missing_key(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тестирует обработку транзакций без ключа currency"""
    modified_transactions: List[Dict[str, Any]] = sample_transactions + [{"amount": 400}]  # type: ignore
    result: List[Dict[str, Any]] = list(filter_by_currency(modified_transactions, "USD"))
    assert len(result) == 2


# Тесты для transaction_descriptions
def test_transaction_descriptions_normal(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тестирует получение описаний транзакций"""
    result: List[Optional[str]] = list(transaction_descriptions(sample_transactions))
    assert result == ["Payment 1", "Payment 2", "Payment 3"]


def test_transaction_descriptions_empty(empty_transactions: List[Dict[str, Any]]) -> None:
    """Тестирует пустой список транзакций"""
    result: List[Any] = list(transaction_descriptions(empty_transactions))
    assert len(result) == 0


def test_transaction_descriptions_missing_desc(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тестирует отсутствие описания"""
    modified_transactions: List[Dict[str, Any]] = sample_transactions + [
        {"amount": 400, "currency": "GBP"}
    ]  # type: ignore
    result: List[Optional[str]] = list(transaction_descriptions(modified_transactions))
    assert result[-1] is None


# Тесты для card_number_generator
def test_card_number_generator_normal() -> None:
    """Тестирует генерацию номеров карт"""
    result: List[str] = list(card_number_generator(1, 5))
    assert result == [
        "0000 0000 0000 0001",
        "0000 0000 0000 0002",
        "0000 0000 0000 0003",
        "0000 0000 0000 0004",
        "0000 0000 0000 0005",
    ]


def test_card_number_generator_format() -> None:
    """Тестирует форматирование номера карты"""
    result: str = next(card_number_generator(1234567890123456, 1234567890123456))
    assert result == "1234 5678 9012 3456"


def test_card_number_generator_edge_cases() -> None:
    """Тестирует крайние значения"""
    min_result: str = next(card_number_generator(1, 1))
    assert min_result == "0000 0000 0000 0001"

    max_result: str = next(card_number_generator(9999999999999999, 9999999999999999))
    assert max_result == "9999 9999 9999 9999"


if __name__ == "__main__":
    pytest.main()
