from typing import Dict, Generator, List, Optional
from unittest.mock import Mock, patch

import pytest

from src.external_api import convert_to_rub


@pytest.fixture
def mock_exchange_api() -> Generator[Mock, None, None]:
    with patch("requests.get") as mock_get:
        yield mock_get


@pytest.fixture
def sample_transactions() -> List[Dict[str, str]]:
    return [
        {"amount": "100", "currency": "RUB"},
        {"amount": "50", "currency": "USD"},
        {"amount": "0", "currency": "EUR"},
        {"amount": "200", "currency": "GBP"},
        {"amount": "300", "currency": "JPY"},
    ]


@pytest.mark.parametrize(
    "currency, rate, expected",
    [
        ("USD", 90.0, 4500.0),
        ("EUR", 100.0, 0.0),
        ("GBP", None, 0.0),
        ("JPY", None, 0.0),
    ],
)
def test_convert_to_rub_with_mock(
    mock_exchange_api: Mock,
    currency: str,
    rate: Optional[float],
    expected: float,
    sample_transactions: List[Dict[str, str]],
) -> None:
    if currency in ("USD", "EUR"):
        mock_exchange_api.return_value.json.return_value = {"rates": {"RUB": rate}}

    transaction = next(t for t in sample_transactions if t["currency"] == currency)
    assert convert_to_rub(transaction) == expected


def test_convert_rub_without_api(sample_transactions: List[Dict[str, str]]) -> None:
    rub_transaction = next(t for t in sample_transactions if t["currency"] == "RUB")
    assert convert_to_rub(rub_transaction) == 100.0
