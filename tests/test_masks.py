import random
from typing import List

import pytest

from src.masks import get_mask_account, get_mask_card_number


@pytest.fixture
def card_number_data() -> List[str]:
    """Фикстура для тестирования номеров карт"""

    def generate_card_number(length: int = 16) -> str:
        return "".join(random.choices("0123456789", k=length))

    return [
        generate_card_number(),  # Стандартная карта
        generate_card_number(15),  # AMEX
        generate_card_number(19),  # Длинный номер
        "",  # Пустая строка
        "1234 5678 9012 3456",  # С пробелами
        "invalid",  # Некорректные данные
        "1234567890",  # Короткий номер
    ]


def test_get_mask_card_number(card_number_data: List[str]) -> None:
    """Тестирует маскировку номеров карт"""
    for number in card_number_data:
        masked = get_mask_card_number(number)

        if not number:
            assert masked == ""
        elif not number.replace(" ", "").isdigit():
            assert masked == number
        else:
            cleaned = number.replace(" ", "")
            if len(cleaned) < 10:
                assert masked == number
            else:
                assert len(masked.replace(" ", "")) == len(cleaned)
                assert masked.replace(" ", "")[:6] == cleaned[:6]
                assert masked.replace(" ", "")[-4:] == cleaned[-4:]
                assert all(c == "*" for c in masked.replace(" ", "")[6:-4])


@pytest.fixture
def account_data() -> List[str]:
    """Фикстура для тестирования номеров счетов"""

    def generate_account(length: int = 20) -> str:
        return "".join(random.choices("0123456789", k=length))

    return [
        generate_account(),  # Стандартный счет
        generate_account(10),  # Короткий счет
        generate_account(25),  # Длинный счет
        "",  # Пустая строка
        "1234 5678 9012 3456",  # С пробелами
        "invalid",  # Некорректные данные
        "123",  # Очень короткий
    ]


def test_get_mask_account(account_data: List[str]) -> None:
    """Тестирует маскировку номеров счетов"""
    for account in account_data:
        masked = get_mask_account(account)

        if not account:
            assert masked == ""
        elif not account.replace(" ", "").isdigit():
            assert masked == account
        else:
            cleaned = account.replace(" ", "")
            if len(cleaned) < 4:
                assert masked == account
            else:
                assert len(masked.replace(" ", "")) == len(cleaned)
                assert masked.replace(" ", "")[-4:] == cleaned[-4:]
                assert all(c == "*" for c in masked.replace(" ", "")[:-4])
