from src.logger_config import get_logger

logger = get_logger("masks")


def mask_credit_card(card_number: str) -> str:
    """Маскирует номер кредитной карты"""
    logger.info(f"Начало маскировки карты: {card_number}")

    try:
        if len(card_number) < 6:
            logger.warning(f"Номер карты слишком короткий: {card_number}")
            return card_number

        masked = card_number[:4] + " **** **** " + card_number[-4:]
        logger.info(f"Карта успешно замаскирована: {masked}")
        return masked

    except Exception as e:
        logger.error(f"Ошибка при маскировке карты: {str(e)}", exc_info=True)
        raise


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
