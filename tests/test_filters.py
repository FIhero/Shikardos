from typing import Dict, List

import pytest

from src.filters import filter_by_description


@pytest.fixture
def sample_transactions() -> List[Dict[str, str]]:
    return [
        {"description": "Перевод организации", "amount": "100"},
        {"description": "Оплата услуг", "amount": "200"},
        {"description": "Открытие вклада", "amount": "300"},
        {"description": "Перевод с карты на карту", "amount": "400"},
    ]


def test_filter_by_description(sample_transactions: List[Dict[str, str]]) -> None:
    result: List[Dict[str, str]] = filter_by_description(sample_transactions, "перевод")
    assert len(result) == 2
    assert all("перевод" in t["description"].lower() for t in result)


def test_filter_by_description_case_insensitive(sample_transactions: List[Dict[str, str]]) -> None:
    result: List[Dict[str, str]] = filter_by_description(sample_transactions, "ПЕРЕВОД")
    assert len(result) == 2


def test_filter_by_description_regex(sample_transactions: List[Dict[str, str]]) -> None:
    result: List[Dict[str, str]] = filter_by_description(sample_transactions, r"перевод\s+организации")
    assert len(result) == 1
    assert result[0]["description"] == "Перевод организации"
