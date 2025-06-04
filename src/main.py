# Все импорты должны быть в начале файла
from src.logger_config import setup_logging
from src.masks import mask_credit_card
from src.utils import format_phone_number

setup_logging()


def main() -> None:
    """Основная функция приложения"""
    card = "1234567890123456"
    phone = "79001234567"

    print(f"Маскированная карта: {mask_credit_card(card)}")
    print(f"Форматированный телефон: {format_phone_number(phone)}")


if __name__ == "__main__":
    main()
