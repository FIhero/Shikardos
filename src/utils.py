import json
from pathlib import Path
from typing import Any, Dict, List

from src.logger_config import get_logger

logger = get_logger("utils")


def format_phone_number(phone: str) -> str:
    """Форматирует номер телефона"""
    logger.info(f"Форматирование номера телефона: {phone}")

    try:
        # Ваша логика форматирования
        formatted = "+7 (" + phone[1:4] + ") " + phone[4:7] + "-" + phone[7:9] + "-" + phone[9:]
        logger.info(f"Номер успешно отформатирован: {formatted}")
        return formatted

    except Exception as e:
        logger.error(f"Ошибка при форматировании номера: {str(e)}", exc_info=True)
        raise


def load_transactions(file_path: str) -> List[Dict[str, Any]]:
    """Загружает транзакции из JSON файла с полной обработкой ошибок."""
    path = Path(file_path)
    if not path.is_file():
        return []

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            return data

    except json.JSONDecodeError:
        return []
    except OSError:
        return []
