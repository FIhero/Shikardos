import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, List

import pandas as pd
import pytest
from _pytest.capture import CaptureFixture
from _pytest.logging import LogCaptureFixture

from src.read_financial_file import read_financial_file


@pytest.fixture
def sample_empty_csv_file(tmp_path: Path) -> Generator[str, None, None]:
    """Создает абсолютно пустой CSV-файл."""
    file_path: Path = tmp_path / "empty.csv"
    file_path.write_text("", encoding="utf-8-sig")
    yield str(file_path)


@pytest.fixture
def sample_csv_file(tmp_path: Path) -> Generator[str, None, None]:
    """Создает образец CSV-файла для тестирования."""
    file_content: str = """date,description,amount,category
2023-01-01,Продукты,50.00,Еда
2023-01-02,Зарплата,1000.00,Доход
"""
    file_path: Path = tmp_path / "test.csv"
    file_path.write_text(file_content, encoding="utf-8-sig")
    yield str(file_path)


@pytest.fixture
def sample_csv_file_no_category(tmp_path: Path) -> Generator[str, None, None]:
    """Создает образец CSV-файла без столбца 'category'."""
    file_content: str = """date,description,amount
2023-01-03,Книги,25.00
2023-01-04,Кофе,5.50
"""
    file_path: Path = tmp_path / "test_no_category.csv"
    file_path.write_text(file_content, encoding="utf-8-sig")
    yield str(file_path)


@pytest.fixture
def sample_xlsx_file(tmp_path: Path) -> Generator[str, None, None]:
    """Создает образец XLSX-файла для тестирования."""
    data: dict = {
        "date": ["2023-02-01", "2023-02-02"],
        "description": ["Аренда", "Коммунальные услуги"],
        "amount": [800.00, 100.00],
        "category": ["Жилье", "Счета"],
    }
    df: pd.DataFrame = pd.DataFrame(data)
    file_path: Path = tmp_path / "test.xlsx"
    df.to_excel(file_path, index=False)
    yield str(file_path)


def test_read_financial_file_csv_success(sample_csv_file: str) -> None:
    """Тестирует чтение корректного CSV-файла."""
    operations: List[dict] = read_financial_file(sample_csv_file)  # Измените тип подсказки
    assert len(operations) == 2
    assert operations[0] == {
        "date": datetime(2023, 1, 1),
        "description": "Продукты",
        "amount": 50.0,
        "category": "Еда",
    }
    assert operations[1] == {
        "date": datetime(2023, 1, 2),
        "description": "Зарплата",
        "amount": 1000.0,
        "category": "Доход",
    }


def test_read_financial_file_csv_no_category(sample_csv_file_no_category: str) -> None:
    """Тестирует чтение CSV-файла без столбца 'category'."""
    operations: List[dict] = read_financial_file(sample_csv_file_no_category)  # Update type hint
    assert len(operations) == 2
    assert operations[0] == {"date": datetime(2023, 1, 3), "description": "Книги", "amount": 25.0, "category": ""}
    assert operations[1] == {"date": datetime(2023, 1, 4), "description": "Кофе", "amount": 5.5, "category": ""}


def test_read_financial_file_xlsx_success(sample_xlsx_file: str) -> None:
    """Тестирует чтение корректного XLSX-файла."""
    operations: List[dict] = read_financial_file(sample_xlsx_file)  # Update type hint
    assert len(operations) == 2
    assert operations[0] == {
        "date": datetime(2023, 2, 1),
        "description": "Аренда",
        "amount": 800.0,
        "category": "Жилье",
    }
    assert operations[1] == {
        "date": datetime(2023, 2, 2),
        "description": "Коммунальные услуги",
        "amount": 100.0,
        "category": "Счета",
    }


def test_read_financial_file_non_existent_file() -> None:
    """Тестирует чтение несуществующего файла."""
    operations: list[dict[Any, Any]] = read_financial_file("non_existent_file.csv")
    assert len(operations) == 0


def test_read_financial_file_unsupported_format(tmp_path: Path) -> None:
    """Тестирует чтение файла с неподдерживаемым форматом."""
    dummy_file: Path = tmp_path / "test.txt"
    dummy_file.write_text("какое-то содержимое", encoding="utf-8-sig")
    operations: list[dict[Any, Any]] = read_financial_file(str(dummy_file))
    assert len(operations) == 0


def test_read_financial_file_empty_csv(sample_empty_csv_file: str) -> None:
    """Тестирует чтение пустого CSV-файла (только заголовки)."""
    operations: list[dict[Any, Any]] = read_financial_file(sample_empty_csv_file)
    assert len(operations) == 0


def test_read_financial_file_malformed_csv(tmp_path: Path, capsys: CaptureFixture, caplog: LogCaptureFixture) -> None:
    """Тестирует чтение CSV-файла с некорректными данными (например, отсутствующими столбцами)."""
    file_content: str = """date,description
2023-03-01,Обед
"""
    file_path: Path = tmp_path / "malformed.csv"
    file_path.write_text(file_content, encoding="utf-8-sig")
    with caplog.at_level(logging.ERROR):
        operations: list[dict[Any, Any]] = read_financial_file(str(file_path))
        assert len(operations) == 0
        assert any("Отсутствуют обязательные колонки: {'amount'}" in record.message for record in caplog.records)


def test_read_financial_file_empty_csv_data_error(sample_empty_csv_file: str, caplog: LogCaptureFixture) -> None:
    """Тестирует чтение CSV-файла, который пуст или содержит только заголовки."""
    with caplog.at_level(logging.INFO):
        operations = read_financial_file(sample_empty_csv_file)
        assert len(operations) == 0
        assert "CSV файл пуст или содержит только заголовки" in caplog.text


def test_read_financial_file_excel_general_exception(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    """Тестирует чтение Excel-файла, вызывающего общую ошибку."""
    bad_excel_content = "This is not an Excel file content."
    file_path = tmp_path / "corrupted.xlsx"
    file_path.write_text(bad_excel_content, encoding="utf-8-sig")

    with caplog.at_level(logging.ERROR):
        operations = read_financial_file(str(file_path))
        assert len(operations) == 0
        assert "Ошибка чтения Excel файла" in caplog.text
        assert "File is not a zip file" in caplog.text or "BadZipFile" in caplog.text


def test_read_financial_file_csv_general_exception(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    """Тестирует чтение CSV-файла, вызывающего общую ошибку (например, ошибку кодировки)."""

    malformed_file_content = "date,description,amount\n2023-01-01,Тест,50.00\n"
    file_path = tmp_path / "malformed_encoding_error.csv"

    try:
        file_path.write_text(malformed_file_content, encoding="cp1251")
    except LookupError:
        file_path.write_text(malformed_file_content, encoding="latin-1")

    with caplog.at_level(logging.ERROR):
        caplog.clear()
        operations = read_financial_file(str(file_path))
        assert len(operations) == 0
        assert "Ошибка чтения CSV файла" in caplog.text
        assert "codec can't decode byte" in caplog.text or "invalid continuation byte" in caplog.text


def test_read_financial_file_invalid_path_type(caplog: LogCaptureFixture) -> None:
    """Тестирует вызов read_financial_file с нестроковым путем."""
    with caplog.at_level(logging.ERROR):
        caplog.clear()
        operations: List[dict[str, Any]]

        operations = read_financial_file(123)  # type: ignore [arg-type]
        assert len(operations) == 0
        assert "Путь к файлу должен быть строкой." in caplog.text

        caplog.clear()

        operations = read_financial_file(None)  # type: ignore [arg-type]
        assert len(operations) == 0
        assert "Путь к файлу должен быть строкой." in caplog.text
