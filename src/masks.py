def get_mask_card_number(card_number: str) -> str:
    if not card_number or not card_number.replace(" ", "").isdigit():
        return card_number
    cleaned = card_number.replace(" ", "")
    if len(cleaned) < 10:  # Минимальная длина для маскировки
        return card_number
    return f"{cleaned[:6]}{'*' * (len(cleaned) - 10)}{cleaned[-4:]}"


def get_mask_account(account: str) -> str:
    """Маскирует номер счёта, оставляя последние 4 цифры и сохраняя исходную длину"""
    if not account:
        return ""
    cleaned = account.replace(" ", "")
    if not cleaned.isdigit():
        return account
    if len(cleaned) < 4:
        return account
    return "*" * (len(cleaned) - 4) + cleaned[-4:]
