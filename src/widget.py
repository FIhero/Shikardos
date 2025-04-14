from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(type_and_number_of_the_card_or_account: str) -> str:
    """Маскирует номер карты/счета в строке формата"""
    parts = type_and_number_of_the_card_or_account.split()
    number = parts[-1]
    description = " ".join(parts[:-1])

    if description.lower().startswith("счет"):
        masked_number = get_mask_account(number)
    else:
        masked_number = get_mask_card_number(number)
    return f"{description} {masked_number}"


def get_date(date_str: str) -> str:
    """Преобразует строку с датой из формата "ГГГГ-ММ-ДДTчч:мм:сс.микросекунды" в формат "ДД.ММ.ГГГГ".
    Кто так даты пишет что их надо аж в нормальный вид приводить?"""
    date_part = date_str.split("T")[0]
    year, month, day = date_part.split("-")
    return f"{day}.{month}.{year}"
