def get_mask_card_number(card_number: str) -> str:
    """Маскирует номер банковской карты, заменяя часть цифр на '*'."""
    if not card_number or not card_number.isdigit():
        return card_number
    elif len(card_number) < 10:
        return card_number
    first_part = card_number[:6]
    last_part = card_number[-4:]
    masked_part = "*" * (len(card_number) - 10)
    return f"{first_part}{masked_part}{last_part}"


def get_mask_account(account: str) -> str:
    """Маскирует счет, оставляя видимыми последние 4 цифры"""
    if not account or not account.isdigit():
        return account
    last_four = account[-4:]
    mask_length = len(account) - 4
    mask = "*" * mask_length
    masked_account = mask + last_four
    return masked_account
