#!/usr/bin/env python3
# modules/data_sync.py
# Утилита для синхронизации данных о пользователях WireGuard

#!/usr/bin/env python3
# modules/data_sync.py

import os
import json
from datetime import datetime

USER_RECORDS_JSON = os.path.join("user", "data", "user_records.json")
WG_USERS_JSON = os.path.join("logs", "wg_users.json")


def load_json(filepath):
    """Загружает данные из JSON-файла."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_json(filepath, data):
    """Сохраняет данные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def sync_user_data():
    """Синхронизирует данные из user_records.json в wg_users.json."""
    user_records = load_json(USER_RECORDS_JSON)
    if not user_records:
        print("❌ No data found in user_records.json.")
        save_json(WG_USERS_JSON, {})  # Сбрасываем wg_users.json
        return {}

    # Подготавливаем данные для wg_users.json
    wg_data = {
        "users": {}
    }

    for username, details in user_records.items():
        wg_data["users"][username] = {
            "allowed_ips": details.get("allowed_ips", "N/A"),
            "endpoint": details.get("endpoint", "N/A"),
            "status": details.get("status", "inactive"),
            "last_handshake": details.get("last_handshake", "N/A"),
            "total_transfer": {
                "received": details.get("downloaded", "N/A"),
                "sent": details.get("uploaded", "N/A")
            }
        }

    # Сохраняем в wg_users.json
    save_json(WG_USERS_JSON, wg_data)
    print(f"✅ wg_users.json updated with {len(wg_data['users'])} users.")
    return wg_data


if __name__ == "__main__":
    sync_user_data()
