from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Generator, List

import pytest
from _pytest.capture import CaptureFixture

import pandas as pd


@dataclass
class FinancialOperation:
    date: datetime
    description: str
    amount: float
    category: str


def read_financial_file(file_path: str) -> List[FinancialOperation]:
    """Читает CSV или XLSX файл и возвращает список финансовых операций."""
    operations: List[FinancialOperation] = []  # Аннотация для списка операций

    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, parse_dates=["date"], encoding="utf-8-sig")
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path, parse_dates=["date"])
        else:
            raise ValueError("Формат файла не поддерживается (ожидается .csv или .xlsx)")

        for _, row in df.iterrows():
            operation = FinancialOperation(
                date=row["date"],
                description=row["description"],
                amount=float(row["amount"]),
                category=row.get("category", ""),
            )
            operations.append(operation)

    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

    return operations


@pytest.fixture
def sample_csv_file(tmp_path: Path) -> Generator[str, None, None]:
    """Создает образец CSV-файла для тестирования."""
    file_content: str = """date,description,amount,category
2023-01-01,Продукты,50.00,Еда
2023-01-02,Зарплата,1000.00,Доход
"""
    file_path: Path = tmp_path / "test.csv"
    file_path.write_text(file_content, encoding="utf-8-sig")
    yield str(file_path)  # Используем yield для фикстур, чтобы они были генераторами


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


@pytest.fixture
def sample_empty_csv_file(tmp_path: Path) -> Generator[str, None, None]:
    """Создает пустой CSV-файл."""
    file_path: Path = tmp_path / "empty.csv"
    file_path.write_text("date,description,amount,category\n", encoding="utf-8-sig")
    yield str(file_path)


def test_read_financial_file_csv_success(sample_csv_file: str) -> None:
    """Тестирует чтение корректного CSV-файла."""
    operations: List[FinancialOperation] = read_financial_file(sample_csv_file)
    assert len(operations) == 2
    assert operations[0] == FinancialOperation(
        date=datetime(2023, 1, 1), description="Продукты", amount=50.0, category="Еда"
    )
    assert operations[1] == FinancialOperation(
        date=datetime(2023, 1, 2), description="Зарплата", amount=1000.0, category="Доход"
    )


def test_read_financial_file_csv_no_category(sample_csv_file_no_category: str) -> None:
    """Тестирует чтение CSV-файла без столбца 'category'."""
    operations: List[FinancialOperation] = read_financial_file(sample_csv_file_no_category)
    assert len(operations) == 2
    assert operations[0] == FinancialOperation(
        date=datetime(2023, 1, 3), description="Книги", amount=25.0, category=""
    )
    assert operations[1] == FinancialOperation(date=datetime(2023, 1, 4), description="Кофе", amount=5.5, category="")


def test_read_financial_file_xlsx_success(sample_xlsx_file: str) -> None:
    """Тестирует чтение корректного XLSX-файла."""
    operations: List[FinancialOperation] = read_financial_file(sample_xlsx_file)
    assert len(operations) == 2
    assert operations[0] == FinancialOperation(
        date=datetime(2023, 2, 1), description="Аренда", amount=800.0, category="Жилье"
    )
    assert operations[1] == FinancialOperation(
        date=datetime(2023, 2, 2), description="Коммунальные услуги", amount=100.0, category="Счета"
    )


def test_read_financial_file_non_existent_file() -> None:
    """Тестирует чтение несуществующего файла."""
    operations: List[FinancialOperation] = read_financial_file("non_existent_file.csv")
    assert len(operations) == 0


def test_read_financial_file_unsupported_format(tmp_path: Path) -> None:
    """Тестирует чтение файла с неподдерживаемым форматом."""
    dummy_file: Path = tmp_path / "test.txt"
    dummy_file.write_text("какое-то содержимое", encoding="utf-8-sig")
    operations: List[FinancialOperation] = read_financial_file(str(dummy_file))
    assert len(operations) == 0


def test_read_financial_file_empty_csv(sample_empty_csv_file: str) -> None:
    """Тестирует чтение пустого CSV-файла (только заголовки)."""
    operations: List[FinancialOperation] = read_financial_file(sample_empty_csv_file)
    assert len(operations) == 0


def test_read_financial_file_malformed_csv(tmp_path: Path, capsys: CaptureFixture) -> None:
    """Тестирует чтение CSV-файла с некорректными данными (например, отсутствующими столбцами)."""
    file_content: str = """date,description
2023-03-01,Обед
"""
    file_path: Path = tmp_path / "malformed.csv"
    file_path.write_text(file_content, encoding="utf-8-sig")
    operations: List[FinancialOperation] = read_financial_file(str(file_path))
    assert len(operations) == 0
    captured = capsys.readouterr()
    assert "Ошибка при чтении файла" in captured.out
    assert "'amount'" in captured.out
