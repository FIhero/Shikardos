from typing import Optional

from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(type_and_number_of_the_card_or_account: str) -> str:
    """Маскирует номер карты/счета в строке формата"""
    if not type_and_number_of_the_card_or_account.strip():
        return type_and_number_of_the_card_or_account

    parts = type_and_number_of_the_card_or_account.split()
    if len(parts) < 2:
        return type_and_number_of_the_card_or_account

    description = " ".join(parts[:-1])
    number = parts[-1]

    if description.lower().startswith("счет"):
        masked_number = get_mask_account(number)
    else:
        masked_number = get_mask_card_number(number)

    return f"{description} {masked_number}"


def get_date(date_str: str) -> Optional[str]:
    """Преобразует строку с датой из формата ISO 8601 в формат ДД.ММ.ГГГГ"""
    if not date_str:
        return None
    try:
        date_part = date_str.split("T")[0]
        year, month, day = date_part.split("-")
        year_num = int(year)
        month_num = int(month)
        day_num = int(day)
        if not (1 <= month_num <= 12):
            return None
        if month_num in {4, 6, 9, 11} and day_num > 30:
            return None
        elif month_num == 2:
            if day_num > 28:
                return None
        elif day_num > 31:
            return None
        return f"{day_num:02d}.{month_num:02d}.{year_num:04}"
    except (ValueError, IndexError):
        return None
