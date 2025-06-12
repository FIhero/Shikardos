from typing import Dict, List

import pytest

from src.counters import count_categories


@pytest.fixture
def sample_transactions() -> List[Dict[str, str]]:
    return [
        {"description": "Перевод организации"},
        {"description": "Оплата услуг"},
        {"description": "Перевод другу"},
        {"description": "Оплата налогов"},
    ]


def test_count_categories(sample_transactions: List[Dict[str, str]]) -> None:
    categories: List[str] = ["перевод", "оплата"]
    result: Dict[str, int] = count_categories(sample_transactions, categories)
    assert result == {"перевод": 2, "оплата": 2}


def test_count_categories_empty(sample_transactions: List[Dict[str, str]]) -> None:
    result: Dict[str, int] = count_categories(sample_transactions, [])
    assert result == {}
