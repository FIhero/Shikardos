def get_mask_card_number(card_number: str) -> str:
    """Маскирует номер банковской карты, заменяя часть цифр на '*'."""
    list_card_number = ""
    for i, card_num in enumerate(card_number):
        if 6 <= i <= 11:
            list_card_number += "*"
        else:
            list_card_number += card_num
    return list_card_number


def get_mask_account(account: str) -> str:
    """маскирует счет, оставляя видимыми последние 4 цифры"""
    last_four = account[-4:]
    mask_length = len(account) - 4
    mask = "*" * mask_length
    masked_account = mask + last_four
    return masked_account
