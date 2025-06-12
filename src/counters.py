from collections import Counter
from typing import Dict, List


def count_categories(transactions: List[Dict], categories: List[str]) -> Dict[str, int]:
    """Подсчитывает количество операций по категориям"""
    descriptions = [t.get("description", "").lower() for t in transactions]
    category_counts: Counter[str] = Counter()

    for category in categories:
        category_lower = category.lower()
        category_counts[category] = sum(1 for desc in descriptions if category_lower in desc)

    return dict(category_counts)
