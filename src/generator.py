from typing import Any, Dict, Iterator, List, Optional


def filter_by_currency(transactions: List[Dict[str, Any]], currency: str) -> Iterator[Dict[str, Any]]:
    """Принимает на вход список словарей, представляющих транзакции."""
    return (transaction for transaction in transactions if transaction.get("currency") == currency)


def transaction_descriptions(transactions: List[Dict[str, Any]]) -> Iterator[Optional[str]]:
    """Принимает список словарей с транзакциями и возвращает описание каждой операции по очереди."""
    return (transaction.get("description") for transaction in transactions)


def card_number_generator(start: int, end: int) -> Iterator[str]:
    """Генерирует номера банковских карт в формате XXXX XXXX XXXX XXXX."""
    for number in range(start, end + 1):
        card_num = f"{number:016d}"
        formatted_num = " ".join([card_num[i: i + 4] for i in range(0, 16, 4)])
        yield formatted_num
