from dataclasses import dataclass
from datetime import datetime
from typing import List

import pandas as pd


@dataclass
class FinancialOperation:
    date: datetime
    description: str
    amount: float
    category: str


def read_financial_file(file_path: str) -> List[FinancialOperation]:
    """Читает CSV или XLSX файл и возвращает список финансовых операций."""
    operations = []

    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, parse_dates=["date"])
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
