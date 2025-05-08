from datetime import datetime

def filter_by_state(data, state="EXECUTED"):
    """Возвращает новый список словарей, содержащий только те словари, у которых ключ
    state соответствует указанному значению"""
    return [item for item in data if item.get("state") == state]


def sort_by_date(data, reverse=True):
    """Возвращает новый список, отсортированный по дате"""
    return sorted(data, key=lambda x: datetime.fromisoformat(x["date"]), reverse=reverse)