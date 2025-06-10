import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@dataclass
class FinancialOperation:
    date: datetime
    description: str
    amount: float
    category: str = ""


def _convert_df_to_operations(df: pd.DataFrame) -> List[dict]:
    """Внутренняя функция преобразования DataFrame в список операций"""
    operations = []
    required_columns = {"date", "description", "amount"}

    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        logging.error(f"Отсутствуют обязательные колонки: {missing}")
        return []

    for index_val, row in df.iterrows():
        if isinstance(index_val, (int)):
            row_index = int(index_val) + 1
        else:
            logging.warning(f"Неожиданный тип индекса строки: {type(index_val)}. Пропускаем.")
            continue

        date_obj: Any = None
        amount_val: Any = None

        try:
            if pd.isna(row["date"]):
                logging.warning(f"Пропущена дата в строке {row_index}. Строка будет пропущена.")
                continue

            try:
                if isinstance(row["date"], datetime):
                    date_obj = row["date"]
                elif isinstance(row["date"], pd.Timestamp):
                    date_obj = row["date"].to_pydatetime()
                elif isinstance(row["date"], str):
                    date_obj = datetime.fromisoformat(row["date"])
                else:
                    logging.warning(
                        f"Неожиданный тип даты в строке {row_index}: {type(row['date'])}. Строка будет пропущена."
                    )
                    continue

            except (ValueError, TypeError, AttributeError) as e:
                logging.warning(f"Ошибка парсинга даты в строке {row_index}: {e}. Строка будет пропущена.")
                continue

            if pd.isna(row["amount"]):
                logging.warning(f"Пропущена сумма в строке {row_index}. Строка будет пропущена.")
                continue

            try:
                amount_val = float(row["amount"])
            except (ValueError, TypeError) as e:
                logging.warning(f"Ошибка преобразования суммы в строке {row_index}: {e}. Строка будет пропущена.")
                continue

            operations.append(
                {
                    "date": date_obj,
                    "description": str(row["description"]),
                    "amount": amount_val,
                    "category": str(row.get("category", "")),
                }
            )
        except Exception as e:
            logging.warning(f"Неожиданная ошибка обработки строки {row_index}: {e}. Строка будет пропущена.")
            continue

    return operations


def read_csv_file(file_path: str) -> List[dict]:
    """Чтение финансовых операций из CSV файла"""
    try:
        df = pd.read_csv(file_path, parse_dates=["date"])
        return _convert_df_to_operations(df)
    except FileNotFoundError:
        logging.info(f"Файл не найден: {file_path}")
        return []
    except pd.errors.EmptyDataError:
        logging.info(f"CSV файл пуст или содержит только заголовки: {file_path}")
        return []
    except Exception as e:
        logging.error(f"Ошибка чтения CSV файла '{file_path}': {e}")
        return []


def read_excel_file(file_path: str) -> List[dict]:
    """Чтение финансовых операций из Excel файла"""
    try:
        df = pd.read_excel(file_path, engine="openpyxl", parse_dates=["date"])
        return _convert_df_to_operations(df)
    except FileNotFoundError:
        logging.info(f"Файл не найден: {file_path}")
        return []
    except Exception as e:
        logging.error(f"Ошибка чтения Excel файла '{file_path}': {e}")
        return []


def read_financial_file(file_path: str) -> List[dict]:
    """Основная функция для чтения финансовых файлов"""
    if not isinstance(file_path, str):
        logging.error("Путь к файлу должен быть строкой.")
        return []

    file_path_lower = file_path.lower()
    if file_path_lower.endswith(".csv"):
        return read_csv_file(file_path)
    elif file_path_lower.endswith((".xlsx", ".xls")):
        return read_excel_file(file_path)
    else:
        logging.info("Поддерживаются только CSV и Excel файлы.")
        return []
