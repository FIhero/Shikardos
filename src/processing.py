from datetime import datetime

    """Возвращает новый список словарей, содержащий только те словари, у которых ключ
    state соответствует указанному значению"""
    return [item for item in data if item.get("state") == state]


    """Возвращает новый список, отсортированный по дате"""
    return sorted(data, key=lambda x: datetime.fromisoformat(x["date"]), reverse=reverse)