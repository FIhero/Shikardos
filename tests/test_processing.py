from typing import Any, Dict, List

import pytest

from src.processing import filter_by_state, sort_by_date


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    """Фикстура с тестовыми транзакциями"""
    return [
        {"id": 1, "date": "2023-11-01T10:00:00", "state": "EXECUTED"},
        {"id": 2, "date": "2023-10-26T18:00:00", "state": "PENDING"},
        {"id": 3, "date": "2023-11-15T14:30:00", "state": "EXECUTED"},
        {"id": 4, "date": "2023-10-26T12:00:00", "state": "CANCELED"},
        {"id": 5, "date": "2023-11-10T09:15:00", "state": "EXECUTED"},
    ]


@pytest.mark.parametrize(
    "state, expected_ids",
    [
        ("EXECUTED", [1, 3, 5]),
        ("PENDING", [2]),
        ("CANCELED", [4]),
        ("COMPLETED", []),
    ],
)
def test_filter_by_state(sample_transactions: List[Dict[str, Any]], state: str, expected_ids: List[int]) -> None:
    """Тестирует фильтрацию по статусу"""
    filtered = filter_by_state(sample_transactions, state)
    assert [t["id"] for t in filtered] == expected_ids
    assert all(t["state"] == state for t in filtered)


def test_filter_by_state_empty() -> None:
    """Тестирует фильтрацию пустого списка"""
    assert filter_by_state([]) == []


def test_sort_by_date(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тестирует сортировку по дате"""
    sorted_asc = sort_by_date(sample_transactions, False)
    assert [t["id"] for t in sorted_asc] == [4, 2, 1, 5, 3]

    sorted_desc = sort_by_date(sample_transactions, True)
    assert [t["id"] for t in sorted_desc] == [3, 5, 1, 2, 4]


def test_sort_by_date_stable() -> None:
    """Тестирует стабильность сортировки"""
    data = [
        {"id": 1, "date": "2023-11-01T10:00:00"},
        {"id": 2, "date": "2023-11-01T10:00:00"},
    ]
    sorted_data = sort_by_date(data)
    assert [t["id"] for t in sorted_data] == [1, 2]


def test_sort_by_date_errors() -> None:
    """Тестирует обработку ошибок"""
    with pytest.raises(KeyError):
        sort_by_date([{"id": 1}])

    with pytest.raises(ValueError):
        sort_by_date([{"id": 1, "date": "invalid"}])
