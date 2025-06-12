import re
from typing import Dict, List


def filter_by_description(transactions: List[Dict], search_string: str) -> List[Dict]:
    """Фильтрует транзакции по строке в описании с использованием регулярных выражений"""
    try:
        pattern = re.compile(search_string, re.IGNORECASE)
        return [t for t in transactions if "description" in t and pattern.search(t["description"])]
    except re.error:
        return []
