"""
format_helpers.py

Модуль вспомогательных функций для работы с датами и временем.
"""

from datetime import datetime


def format_time(iso_time: str) -> str:
    """
    Форматирует время из ISO 8601 в читаемый формат.
    """
    try:
        dt = datetime.fromisoformat(iso_time)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "N/A"


def calculate_time_remaining(expiry_time: str) -> str:
    """
    Вычисляет оставшееся время до истечения.
    """
    try:
        dt_expiry = datetime.fromisoformat(expiry_time)
        delta = dt_expiry - datetime.now()
        if delta.days >= 0:
            return f"{delta.days} days"
        return "Expired"
    except Exception:
        return "N/A"
