import copy
import random
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pytest

from src.masks import get_mask_account, get_mask_card_number
from src.processing import filter_by_state, sort_by_date
from src.widget import get_date, mask_account_card


@pytest.fixture
def card_number_data() -> List[str]:
    """Генерирует разнообразные тестовые данные для номеров карт."""

    def generate_card_number(length: int = 16) -> str:
        """Генерирует случайный номер карты"""
        card_number = "".join(random.choices("0123456789", k=length))
        return card_number

    test_data = [
        generate_card_number(),
        generate_card_number(),
        generate_card_number(),
        generate_card_number(length=12),
        generate_card_number(length=19),
        "",
        "invalid_input",
        "1234 5678 9012 3456",
        generate_card_number(length=random.randint(10, 20)),
    ]
    return test_data


def test_get_mask_card_number(card_number_data: List[str]) -> None:
    """Тестирует функцию маскирования номера карты."""
    for card_number in card_number_data:
        masked_number = get_mask_card_number(card_number)
        print(f"Original: {card_number!r}, Masked: {masked_number!r}")

        if not card_number:
            assert masked_number == "", "Пустой номер → пустая строка"
        elif not card_number.isdigit():
            assert masked_number == card_number, "Некорректный ввод должен возвращаться без изменений"
        else:
            assert len(masked_number) == len(card_number), "Длина должна совпадать"
            assert masked_number[:6] == card_number[:6], "Первые 6 цифр должны быть видны"
            assert masked_number[-4:] == card_number[-4:], "Последние 4 цифры должны быть видны"
            assert all(c == "*" for c in masked_number[6:-4]), "Не все символы замаскированы"


@pytest.fixture
def account_data() -> List[str]:
    """Генерирует счет"""

    def generate_account_data(length: int = 20) -> str:
        """Генерирует случайный номер счета"""
        account = "".join(random.choices("0123456789", k=length))
        return account

    test_data = [
        generate_account_data(),
        generate_account_data(length=15),
        generate_account_data(length=25),
        "",
        "invalid_input",
        "123",
    ]
    return test_data


def test_get_mask_account(account_data: List[str]) -> None:
    """Тестирование правильности маскирования номера счета."""
    for account in account_data:
        masked_account = get_mask_account(account)
        print(f"Original: {account}, Masked: {masked_account}")

        if not account:
            assert masked_account == ""
        elif not account.isdigit():
            assert masked_account == account, "Некорректный ввод должен возвращаться без изменений"
        else:
            assert len(masked_account) == len(account), "Длина замаскированного номера должна совпадать с оригиналом"
            assert masked_account[-4:] == account[-4:], "Последние 4 цифры должны быть не замаскированы"
            assert all(c == "*" for c in masked_account[:-4]), "Не все символы, кроме последних 4, замаскирован"

            if " " in account:
                assert " " in masked_account, "Пробелы должны сохраняться"
                for orig_char, masked_char in zip(account, masked_account):
                    if orig_char == " ":
                        assert masked_char == " ", "Пробелы должны быть на тех же позициях"


@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        ("Visa Platinum 1234567890123456", "Visa Platinum 123456******3456"),
        ("МИР 1234567890123456", "МИР 123456******3456"),
        ("MasterCard 9876543210987654", "MasterCard 987654******7654"),
        ("American Express 123456789012345", "American Express 123456*****2345"),
        ("Счет 12345678901234567890", "Счет ****************7890"),
        ("счет 98765432109876543210", "счет ****************3210"),
        ("Карта 1234", "Карта 1234"),
        ("Счет 123", "Счет 123"),
        ("", ""),
        ("   ", "   "),
        ("Счет", "Счет"),
        ("Карта", "Карта"),
        ("Invalid 1234567890", "Invalid 1234567890"),
    ],
    ids=[
        "Visa_card",
        "MIR_card",
        "MasterCard_card",
        "AmEx_card",
        "Account_1",
        "Account_2",
        "Short_card_number",
        "Short_account_number",
        "Empty_string",
        "Spaces",
        "Account_no_number",
        "Card_no_number",
        "Unknown_type",
    ],
)
def test_mask_account_card_valid_input(input_data: str, expected_output: str) -> None:
    """Параметризованный тест для проверки корректной маскировки карт и счетов."""
    assert mask_account_card(input_data) == expected_output


def test_mask_account_card_case_insensitive() -> None:
    """Проверка регистронезависимости определения типа счета."""
    assert mask_account_card("сЧеТ 12345678901234567890") == "сЧеТ ****************7890"


@pytest.mark.parametrize(
    "invalid_input",
    [
        1234567890,  # Число вместо строки
        None,  # None
        ["Visa 1234"],  # Список вместо строки
    ],
    ids=[
        "number_input",
        "none_input",
        "list_input",
    ],
)
@pytest.mark.parametrize(
    "invalid_input",
    [
        pytest.param(1234567890, id="number_input"),
        pytest.param(None, id="none_input"),
        pytest.param(["Visa 1234"], id="list_input"),
    ],
)
def test_mask_account_card_invalid_input(invalid_input: Any) -> None:
    """Тестирование невалидных входных данных."""
    with pytest.raises((AttributeError, TypeError)):
        mask_account_card(invalid_input)


def test_mask_account_card_original_unchanged() -> None:
    """Проверка что исходная строка не изменяется."""
    original = "Visa Platinum 1234567890123456"
    input_data = original[:]
    _ = mask_account_card(input_data)
    assert input_data == original


@pytest.fixture
def date_data() -> List[Tuple[str, Optional[str]]]:
    return [
        ("2023-02-16", "16.02.2023"),
        ("2023-02-16T12:34:56", "16.02.2023"),
        ("2023-02-16T12:34:56.123456", "16.02.2023"),
        ("2023-02-16T12:34:56Z", "16.02.2023"),
        ("2023-02-16T12:34:56+03:00", "16.02.2023"),
        ("0001-01-01", "01.01.0001"),
        ("9999-12-31", "31.12.9999"),
        ("2023-04-30", "30.04.2023"),
        ("2023-02-28", "28.02.2023"),
        ("", None),
        ("2023/02/16", None),
        ("2023-13-01", None),
        ("2023-02-30", None),
        ("2023-04-31", None),
        ("hello", None),
        ("2023-02", None),
    ]


def test_get_date(date_data: List[Tuple[str, Optional[str]]]) -> None:
    for input_date, expected in date_data:
        result = get_date(input_date)
        assert result == expected, f"Ошибка для '{input_date}': ожидалось {expected}, получено {result}"


@pytest.fixture
def sample_data() -> List[Dict[str, Any]]:
    """Создает пример списка словарей для тестирования."""
    return [
        {"id": 1, "amount": 100, "state": "EXECUTED"},
        {"id": 2, "amount": 200, "state": "PENDING"},
        {"id": 3, "amount": 300, "state": "EXECUTED"},
        {"id": 4, "amount": 400, "state": "CANCELED"},
        {"id": 5, "amount": 500, "state": "EXECUTED"},
    ]


@pytest.mark.parametrize(
    "state, expected_count",
    [
        ("EXECUTED", 3),
        ("PENDING", 1),
        ("CANCELED", 1),
        ("COMPLETED", 0),
    ],
)
def test_filter_by_state_parameterized(sample_data: List[Dict[str, Any]], state: str, expected_count: int) -> None:
    """Тестирует функцию filter_by_state с параметризацией статусов."""
    filtered_data = filter_by_state(sample_data, state=state)
    assert len(filtered_data) == expected_count, f"Ожидалось {expected_count} элементов со state {state}"
    for item in filtered_data:
        assert item["state"] == state, f"Все элементы должны иметь state {state}"


def test_filter_by_state_empty_data() -> None:
    """Тестирует функцию filter_by_state с пустым списком данных."""
    filtered_data = filter_by_state([])
    assert len(filtered_data) == 0, "При пустом списке должен вернуться пустой список"


def test_filter_by_state_invalid_data() -> None:
    """Тестирует функцию filter_by_state с данными, в которых отсутствует ключ "state"."""
    data = [{"id": 1, "amount": 100}, {"id": 2, "amount": 200}]
    filtered_data = filter_by_state(data)
    assert len(filtered_data) == 0, "Должен вернуться пустой список, если отсутствует ключ state"


def test_sort_by_date_descending(sample_data: List[Dict[str, Any]]) -> None:
    """Тестирует сортировку по датам в порядке убывания"""
    sorted_data = sort_by_date(sample_data)
    expected = sorted(sample_data, key=lambda x: datetime.fromisoformat(x["date"]), reverse=True)
    assert sorted_data == expected
    assert [item["id"] for item in sorted_data] == [3, 5, 1, 2, 4]


def test_sort_by_date_ascending(sample_data: List[Dict[str, Any]]) -> None:
    """Тестирует сортировку по датам в порядке возрастания"""
    sorted_data = sort_by_date(sample_data, reverse=False)
    expected = sorted(sample_data, key=lambda x: datetime.fromisoformat(x["date"]), reverse=False)
    assert sorted_data == expected
    assert [item["id"] for item in sorted_data] == [4, 2, 1, 5, 3]


def test_sort_by_date_stable_sorting() -> None:
    """Тестирует стабильность сортировки при одинаковых датах."""
    data = [
        {"id": 1, "date": "2023-11-01T10:00:00"},
        {"id": 2, "date": "2023-10-26T18:00:00"},
        {"id": 3, "date": "2023-11-01T10:00:00"},
        {"id": 4, "date": "2023-10-26T12:00:00"},
    ]

    sorted_desc = sort_by_date(data)
    assert [item["id"] for item in sorted_desc] == [1, 3, 2, 4]

    sorted_asc = sort_by_date(data, reverse=False)
    assert [item["id"] for item in sorted_asc] == [4, 2, 1, 3]


def test_sort_by_date_edge_cases() -> None:
    """Тестирует крайние случаи."""
    assert sort_by_date([]) == []

    single = [{"id": 1, "date": "2023-11-01T10:00:00"}]
    assert sort_by_date(single) == single


def test_sort_by_date_error_handling() -> None:
    """Тестирует обработку ошибок."""
    with pytest.raises(ValueError):
        sort_by_date([{"id": 1, "date": "01/11/2023"}])

    with pytest.raises(KeyError):
        sort_by_date([{"id": 1}])

    with pytest.raises(ValueError, match="Некорректный формат даты"):
        sort_by_date([{"id": 1, "date": "01/11/2023"}])


def test_sort_by_date_immutability(sample_data: List[Dict[str, Any]]) -> None:
    """Проверяет, что исходные данные не изменяются."""
    original = copy.deepcopy(sample_data)
    sort_by_date(sample_data)
    assert sample_data == original
