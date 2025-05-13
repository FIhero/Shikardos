from typing import Optional

from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(type_and_number: Optional[str]) -> Optional[str]:
    """Маскирует номер карты/счёта"""
    if type_and_number is None:
        return None
    if not isinstance(type_and_number, str):
        return None
    type_and_number = type_and_number.strip()
    if not type_and_number:
        return ""
    parts = type_and_number.rsplit(" ", 1)
    if len(parts) < 2:
        return type_and_number
    description, number = parts
    try:
        if "счет" in description.lower():
            masked = get_mask_account(number)
            if masked is None:
                if len(number) <= 4:
                    masked = "*" * len(number)
                else:
                    masked = "*" * (len(number) - 4) + number[-4:]
        else:
            masked = get_mask_card_number(number)
            if masked is None:
                if len(number) <= 10:
                    masked = number
                else:
                    masked = number[:6] + "*" * (len(number) - 10) + number[-4:]
            else:
                masked = masked.replace(" ", "")
        return f"{description} {masked}"
    except Exception:
        return type_and_number


def get_date(date_str: Optional[str]) -> Optional[str]:
    """Преобразует дату из ISO 8601 в ДД.ММ.ГГГГ с валидацией"""
    if date_str is None:
        return None

    try:
        if "T" not in date_str:
            return None

        date_part = date_str.split("T")[0]
        year, month, day = date_part.split("-")
        year_num, month_num, day_num = int(year), int(month), int(day)

        # Валидация даты
        if not (1 <= month_num <= 12):
            return None

        if month_num in {4, 6, 9, 11} and day_num > 30:
            return None

        if month_num == 2:
            is_leap = (year_num % 4 == 0 and year_num % 100 != 0) or (year_num % 400 == 0)
            if day_num > 29 or (day_num == 29 and not is_leap):
                return None
        elif day_num > 31:
            return None

        return f"{day_num:02d}.{month_num:02d}.{year_num}"
    except (ValueError, IndexError, AttributeError):
        return None
