import json
import os
import sys
from pathlib import Path
from typing import Dict, List
from unittest.mock import patch

import pandas as pd
import pytest

from src.main import (
    load_transactions_from_csv,
    load_transactions_from_json,
    load_transactions_from_xlsx,
    main,
    print_transactions,
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def mock_transactions_data() -> List[Dict]:
    """Фикстура, предоставляющая тестовые данные транзакций."""
    return [
        {
            "id": 1,
            "state": "EXECUTED",
            "date": "2019-12-08T22:45:06.000000",
            "operationAmount": {"amount": "40542.00", "currency": {"name": "руб.", "code": "RUB"}},
            "description": "Открытие вклада",
            "to": "Счет **4321",
        },
        {
            "id": 2,
            "state": "EXECUTED",
            "date": "2019-11-12T19:35:28.000000",
            "operationAmount": {"amount": "130.00", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод с карты на карту",
            "from": "MasterCard 7771 27** **** 3727",
            "to": "Visa Platinum 1293 38** **** 9203",
        },
        {
            "id": 3,
            "state": "CANCELED",
            "date": "2018-07-18T18:05:00.000000",
            "operationAmount": {"amount": "8390.00", "currency": {"name": "руб.", "code": "RUB"}},
            "description": "Перевод организации",
            "from": "Visa Platinum 7492 65** **** 7202",
            "to": "Счет **0034",
        },
        {
            "id": 4,
            "state": "PENDING",
            "date": "2018-06-03T10:30:15.000000",
            "operationAmount": {"amount": "8200.00", "currency": {"name": "EUR", "code": "EUR"}},
            "description": "Перевод со счета на счет",
            "from": "Счет **2935",
            "to": "Счет **4321",
        },
    ]


def test_main_loads_json_and_filters_executed(
    capsys: pytest.CaptureFixture, mock_transactions_data: List[Dict]
) -> None:
    """
    Тест: загрузка JSON, фильтрация по EXECUTED, без сортировки, без руб., без описания.
    """
    with patch(
        "builtins.input",
        side_effect=[
            "1",
            "data/operations.json",
            "EXECUTED",
            "нет",
            "нет",
            "нет",
        ],
    ):
        with patch("src.main.load_transactions_from_json", return_value=mock_transactions_data) as mock_load_json:
            main()
            mock_load_json.assert_called_once_with("data/operations.json")

            captured = capsys.readouterr()
            output = captured.out

            assert "Привет! Добро пожаловать" in output
            assert 'Операции отфильтрованы по статусу "EXECUTED"' in output
            assert "Всего банковских операций в выборке: 2" in output
            assert "Открытие вклада" in output
            assert "Перевод с карты на карту" in output
            assert "Перевод организации" not in output
            assert "Перевод со счета на счет" not in output


def test_main_handles_invalid_status_input(capsys: pytest.CaptureFixture, mock_transactions_data: List[Dict]) -> None:
    """
    Тест: некорректный ввод статуса, затем корректный.
    """
    with patch(
        "builtins.input", side_effect=["1", "data/operations.json", "INVALID_STATUS", "EXECUTED", "нет", "нет", "нет"]
    ):
        with patch("src.main.load_transactions_from_json", return_value=mock_transactions_data):
            main()
            captured = capsys.readouterr()
            output = captured.out

            assert 'Статус операции "INVALID_STATUS" недоступен.' in output
            assert "Введите статус, по которому необходимо выполнить фильтрацию." in output
            assert 'Операции отфильтрованы по статусу "EXECUTED"' in output


def test_main_filters_by_description(capsys: pytest.CaptureFixture, mock_transactions_data: List[Dict]) -> None:
    """
    Тест: фильтрация по слову в описании (например, "перевод").
    """
    with patch("builtins.input", side_effect=["1", "data/operations.json", "EXECUTED", "нет", "нет", "да", "перевод"]):
        with patch("src.main.load_transactions_from_json", return_value=mock_transactions_data):
            main()
            captured = capsys.readouterr()
            output = captured.out

            assert "Всего банковских операций в выборке: 1" in output
            assert "Перевод с карты на карту" in output
            assert "Открытие вклада" not in output


def test_main_sorts_by_date_ascending(capsys: pytest.CaptureFixture, mock_transactions_data: List[Dict]) -> None:
    """
    Тест: сортировка по дате по возрастанию.
    """
    with patch(
        "builtins.input", side_effect=["1", "data/operations.json", "EXECUTED", "да", "по возрастанию", "нет", "нет"]
    ):
        with patch("src.main.load_transactions_from_json", return_value=mock_transactions_data):
            main()
            captured = capsys.readouterr()
            output_lines = captured.out.splitlines()
            start_index = -1
            for i, line in enumerate(output_lines):
                if "Всего банковских операций в выборке:" in line:
                    start_index = i + 1
                    break

            assert start_index != -1, "Не удалось найти начало списка транзакций в выводе."
            transaction_output_lines = []
            for i in range(start_index, len(output_lines)):
                if output_lines[i].strip():
                    transaction_output_lines.append(output_lines[i])
                else:
                    break
            assert (
                len(transaction_output_lines) >= 2
            ), f"Ожидалось как минимум 2 транзакции, найдено: {len(transaction_output_lines)}"
            assert "2019-11-12" in transaction_output_lines[0]
            assert "2019-12-08" in transaction_output_lines[1]


def test_main_displays_old_features(capsys: pytest.CaptureFixture) -> None:
    """
    Тест: демонстрация старых функций (маскирование/форматирование).
    """
    with patch("builtins.input", side_effect=["4", "1", "data/operations.json", "EXECUTED", "нет", "нет", "нет"]):
        with patch(
            "src.main.load_transactions_from_json",
            return_value=[{"id": 999, "state": "EXECUTED", "description": "Dummy transaction"}],
        ):
            with (
                patch("src.main.mask_credit_card", side_effect=lambda x: f"MOCKED_CARD_{x[-4:]}") as mock_mask_card,
                patch(
                    "src.main.format_phone_number", side_effect=lambda x: f"MOCKED_PHONE_{x[-4:]}"
                ) as mock_format_phone,
            ):
                main()
                captured = capsys.readouterr()
                output = captured.out

                assert "--- Демонстрация старых функций ---" in output
                assert "Маскированная карта: MOCKED_CARD_3456" in output
                assert "Форматированный телефон: MOCKED_PHONE_3210" in output
                assert "Привет! Добро пожаловать" in output
                mock_mask_card.assert_called_once()
                mock_format_phone.assert_called_once()


def test_load_transactions_from_json_success(tmp_path: Path, mock_transactions_data: List[Dict]) -> None:
    """Тест успешной загрузки JSON-файла."""
    test_filepath = tmp_path / "test_transactions.json"
    with open(test_filepath, "w", encoding="utf-8") as f:
        json.dump(mock_transactions_data, f, ensure_ascii=False, indent=4)

    transactions = load_transactions_from_json(str(test_filepath))
    assert transactions == mock_transactions_data


def test_load_transactions_from_json_file_not_found(capsys: pytest.CaptureFixture, tmp_path: Path) -> None:
    """Тест: файл JSON не найден."""
    non_existent_path = tmp_path / "non_existent.json"
    transactions = load_transactions_from_json(str(non_existent_path))
    assert transactions == []
    captured = capsys.readouterr()
    assert f"Ошибка: Файл {non_existent_path} не найден." in captured.out


def test_load_transactions_from_csv_success(tmp_path: Path) -> None:
    test_csv_content = (
        """id,state,date,description,operationAmount.amount,operationAmount.currency.name,operationAmount.currency.code,from,to
1,EXECUTED,2023-01-01T10:00:00.000000,Покупка,100.00,руб.,RUB,,Счет **1234
2,EXECUTED,2023-01-02T11:00:00.000000,Перевод,50.00,USD,USD,Visa 1234 56** **** 7890,MasterCard 9876 54** **** 3210
""")
    test_filepath = tmp_path / "test.csv"
    test_filepath.write_text(test_csv_content, encoding="utf-8")
    transactions = load_transactions_from_csv(str(test_filepath))
    assert len(transactions) == 2
    assert transactions[0]["description"] == "Покупка"
    assert transactions[1]["operationAmount"]["amount"] == "50.00"
    assert transactions[1]["operationAmount"]["currency"]["code"] == "USD"


def test_load_transactions_from_xlsx_success() -> None:
    """Для мокирования pandas.read_excel, нужно создать mock DataFrame"""
    mock_df = pd.DataFrame([{"id": 1, "state": "EXECUTED", "description": "XLSX Test"}])
    with patch("pandas.read_excel", return_value=mock_df):
        transactions = load_transactions_from_xlsx("dummy.xlsx")
        assert transactions == [{"id": 1, "state": "EXECUTED", "description": "XLSX Test"}]


def test_print_transactions_empty(capsys: pytest.CaptureFixture) -> None:
    """Тест: print_transactions с пустым списком."""
    print_transactions([])
    captured = capsys.readouterr()
    assert "Не найдено ни одной транзакции, подходящей под ваши условия фильтрации." in captured.out


def test_print_transactions_with_data(capsys: pytest.CaptureFixture) -> None:
    """Тест: print_transactions с данными."""
    transactions = [
        {
            "id": 1,
            "state": "EXECUTED",
            "date": "2023-01-01T10:00:00.000000",
            "operationAmount": {"amount": "100.00", "currency": {"name": "руб.", "code": "RUB"}},
            "description": "Покупка",
            "to": "Счет **1234",
        },
        {
            "id": 2,
            "state": "EXECUTED",
            "date": "2023-01-02T11:00:00.000000",
            "operationAmount": {"amount": "50.00", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод",
            "from": "Visa 1234 56** **** 7890",
            "to": "MasterCard 9876 54** **** 3210",
        },
    ]
    with patch("src.masks.mask_credit_card", side_effect=lambda x: f"MOCKED_{x[-4:]}"):
        print_transactions(transactions)
        captured = capsys.readouterr()
        output = captured.out

        assert "Всего банковских операций в выборке: 2" in output
        assert "2023-01-01 Покупка Счет **** **** 1234 Сумма: 100.00 руб." in output
        assert "2023-01-02 Перевод Visa **** **** 7890 -> Mast **** **** 3210 Сумма: 50.00 USD" in output
