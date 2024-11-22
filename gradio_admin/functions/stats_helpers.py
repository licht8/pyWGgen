"""
stats_helpers.py

Функции для работы со статистикой пользователей WireGuard.
"""

import json
import os
from .format_helpers import format_time, calculate_time_remaining

# Путь к user_records.json
USER_RECORDS_PATH = os.path.join(os.path.dirname(__file__), "../../user/data/user_records.json")


def load_user_records() -> dict:
    """
    Загружает данные о пользователях из файла user_records.json.
    """
    try:
        with open(USER_RECORDS_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[DEBUG] user_records.json not found!")
        return {}
    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON decode error in user_records.json: {e}")
        return {}


def get_user_info(username: str) -> dict:
    """
    Возвращает информацию о пользователе.
    """
    records = load_user_records()
    return records.get(username, {})


def format_user_data(user_data: dict, row: list) -> str:
    """
    Форматирует строку данных о пользователе.
    """
    created = user_data.get("created_at", "N/A")
    expires = user_data.get("expires_at", "N/A")
    int_ip = user_data.get("address", "N/A")
    ext_ip = row[1] if len(row) > 1 else "N/A"
    up = row[4] if len(row) > 4 else "N/A"
    down = row[3] if len(row) > 3 else "N/A"
    state = row[6] if len(row) > 6 else "N/A"

    return f"""
👤 User: {row[0]}
📧 Email: user@mail.wg
🌱 Created: {format_time(created)}
🔥 Expires: {format_time(expires)}
🌐 Internal IP: {int_ip}
🌎 External IP: {ext_ip}
⬆️ Uploaded: {up}
⬇️ Downloaded: {down}
✅ Status: {state}
"""
