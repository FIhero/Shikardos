import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.apilayer.com/exchangerates_data/latest"


def convert_to_rub(transaction: dict) -> float:
    """Конвертирует сумму транзакции в рубли"""
    amount = float(transaction["amount"])
    currency = transaction.get("currency", "RUB").upper()

    if currency == "RUB":
        return amount
    elif currency not in ("USD", "EUR"):
        return 0.0

    try:
        response = requests.get(
            BASE_URL, params={"base": currency, "symbols": "RUB"}, headers={"apikey": API_KEY}, timeout=10
        )
        response.raise_for_status()
        rate = float(response.json()["rates"]["RUB"])
        return amount * rate
    except Exception:
        return 0.0
