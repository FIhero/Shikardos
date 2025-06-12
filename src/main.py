import csv
import json
import os
from typing import Dict, List

import pandas as pd

from src.filters import filter_by_description
from src.logger_config import setup_logging
from src.masks import mask_credit_card
from src.utils import format_phone_number

setup_logging()


def load_transactions_from_json(filepath: str) -> List[Dict]:
    """Загружает транзакции из JSON-файла."""
    if not os.path.exists(filepath):
        print(f"Ошибка: Файл {filepath} не найден.")
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                return data
            else:
                print(f"Ошибка: Некорректный формат данных в файле {filepath}.")
                return []
    except json.JSONDecodeError:
        print(f"Ошибка: Некорректный JSON формат в файле {filepath}.")
        return []
    except Exception as e:
        print(f"Произошла непредвиденная ошибка при чтении файла: {e}")
        return []


def load_transactions_from_csv(filepath: str) -> List[Dict]:
    transactions = []
    try:
        with open(filepath, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                transaction = {k: v for k, v in row.items() if v is not None}
                if (
                    "operationAmount.amount" in transaction
                    and "operationAmount.currency.name" in transaction
                    and "operationAmount.currency.code" in transaction
                ):
                    amount = transaction.pop("operationAmount.amount")
                    currency_name = transaction.pop("operationAmount.currency.name")
                    currency_code = transaction.pop("operationAmount.currency.code")
                    transaction["operationAmount"] = {
                        "amount": amount,
                        "currency": {"name": currency_name, "code": currency_code},
                    }
                transactions.append(transaction)
    except FileNotFoundError:
        print(f"Ошибка: Файл {filepath} не найден.")
    except Exception as e:
        print(f"Произошла ошибка при чтении CSV-файла {filepath}: {e}")
    return transactions


def load_transactions_from_xlsx(filepath: str) -> List[Dict]:
    transactions = []
    try:
        df = pd.read_excel(filepath)
        transactions = df.to_dict("records")
    except FileNotFoundError:
        print(f"Ошибка: Файл {filepath} не найден. Проверьте путь.")
    except Exception as e:
        print(f"Произошла ошибка при чтении XLSX-файла {filepath}: {e}")
    return transactions


def print_transactions(transactions: List[Dict]) -> None:
    """Печатает отформатированный список транзакций."""
    if not transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации.")
        return

    print(f"\nВсего банковских операций в выборке: {len(transactions)}")
    for t in transactions:
        date_str = t.get("date", "")
        if date_str:
            date_str = date_str.split("T")[0]

        description = t.get("description", "Нет описания")
        amount = t.get("operationAmount", {}).get("amount", "N/A")
        currency = t.get("operationAmount", {}).get("currency", {}).get("name", "")
        from_acc = t.get("from", "")
        to_acc = t.get("to", "")

        from_masked = mask_credit_card(from_acc) if from_acc else ""
        to_masked = mask_credit_card(to_acc) if to_acc else ""

        if from_masked and to_masked:
            print(f"{date_str} {description} {from_masked} -> {to_masked} Сумма: {amount} {currency}")
        elif to_masked:
            print(f"{date_str} {description} {to_masked} Сумма: {amount} {currency}")
        else:
            print(f"{date_str} {description} Сумма: {amount} {currency}")


def display_old_features() -> None:
    print("--- Демонстрация старых функций ---")
    masked_card = mask_credit_card("1234567890123456")
    print(f"Маскированная карта: {masked_card}")
    formatted_phone = format_phone_number("+79876543210")
    print(f"Форматированный телефон: {formatted_phone}")


def main() -> None:
    """Основная функция приложения, управляющая пользовательским интерфейсом."""
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")

    transactions: List[Dict] = []
    while not transactions:
        print("Выберите необходимый пункт меню:")
        print("1. Получить информацию о транзакциях из JSON-файла")
        print("2. Получить информацию о транзакциях из CSV-файла")
        print("3. Получить информацию о транзакциях из XLSX-файла")  # Обновлено
        print("4. Демонстрация старых функций (маскирование/форматирование)")
        choice = input("Пользователь: ")

        if choice == "1":
            print("Для обработки выбран JSON-файл.")
            transactions_filepath = input("Введите путь к JSON-файлу (например, data/transactions.json): ")
            transactions = load_transactions_from_json(transactions_filepath)
            if not transactions:
                print("Не удалось загрузить транзакции. Попробуйте снова.")
        elif choice == "2":
            print("Для обработки выбран CSV-файл.")
            transactions_filepath = input("Введите путь к CSV-файлу (например, data/transactions.csv): ")
            transactions = load_transactions_from_csv(transactions_filepath)
            print("Чтение CSV пока не реализовано. Выберите другой вариант.")
        elif choice == "3":
            print("Для обработки выбран XLSX-файл.")
            transactions_filepath = input("Введите путь к XLSX-файлу (например, data/transactions.xlsx): ")
            transactions = load_transactions_from_xlsx(transactions_filepath)
            if not transactions:
                print("Не удалось загрузить транзакции. Попробуйте снова.")
        elif choice == "4":
            return display_old_features()
        else:
            print("Некорректный выбор. Попробуйте снова.")

    filtered_transactions = list(transactions)

    available_statuses = ["EXECUTED", "CANCELED", "PENDING"]
    while True:
        print(
            "Введите статус, по которому необходимо выполнить фильтрацию. Доступные для фильтровки статусы:",
            ", ".join(available_statuses),
        )
        status_input = input("Пользователь: ").upper()

        if status_input in available_statuses:
            filtered_transactions = [t for t in filtered_transactions if t.get("state", "").upper() == status_input]
            print(f'Операции отфильтрованы по статусу "{status_input}"')
            break
        else:
            print(f'Статус операции "{status_input}" недоступен.')

    while True:
        sort_choice = input("Отсортировать операции по дате? Да/Нет Пользователь: ").lower()
        if sort_choice in ["да", "нет"]:
            break
        else:
            print("Некорректный ввод. Пожалуйста, введите 'Да' или 'Нет'.")

    if sort_choice == "да":
        while True:
            order_choice = input("Отсортировать по возрастанию или по убыванию? Пользователь: ").lower()
            if order_choice in ["по возрастанию", "по убыванию"]:
                reverse_sort = order_choice == "по убыванию"
                filtered_transactions.sort(key=lambda t: t.get("date", ""), reverse=reverse_sort)
                break
            else:
                print("Некорректный ввод. Пожалуйста, введите 'по возрастанию' или 'по убыванию'.")

    while True:
        currency_choice = input("Выводить только рублевые транзакции? Да/Нет Пользователь: ").lower()
        if currency_choice in ["да", "нет"]:
            break
        else:
            print("Некорректный ввод. Пожалуйста, введите 'Да' или 'Нет'.")

    if currency_choice == "да":
        filtered_transactions = [
            t
            for t in filtered_transactions
            if t.get("operationAmount", {}).get("currency", {}).get("code", "").upper() == "RUB"
        ]

    while True:
        desc_filter_choice = input(
            "Отфильтровать список транзакций по определенному слову в описании? Да/Нет Пользователь: "
        ).lower()
        if desc_filter_choice in ["да", "нет"]:
            break
        else:
            print("Некорректный ввод. Пожалуйста, введите 'Да' или 'Нет'.")

    if desc_filter_choice == "да":
        search_term = input("Введите слово для поиска в описании: Пользователь: ")
        filtered_transactions = filter_by_description(filtered_transactions, search_term)

    print("Распечатываю итоговый список транзакций...")
    print_transactions(filtered_transactions)


if __name__ == "__main__":
    main()
