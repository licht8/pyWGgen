#!/usr/bin/env python3
# gradio_admin/functions/table_helpers.py

import os
import json
import pandas as pd
from settings import USER_DB_PATH  # Путь к JSON с данными пользователей


def load_data(show_inactive=True):
    """Загружает данные пользователей из JSON."""
    if not os.path.exists(USER_DB_PATH):
        return []

    with open(USER_DB_PATH, "r") as f:
        users = json.load(f)

    table = []
    for username, user_info in users.items():
        if not show_inactive and user_info.get("status", "") != "active":
            continue
        table.append({
            "username": user_info.get("username", "N/A"),
            "data_used": user_info.get("data_used", "0.0 KiB"),
            "data_limit": user_info.get("data_limit", "100.0 GB"),
            "status": user_info.get("status", "inactive"),
            "subscription_price": user_info.get("subscription_price", "0.00 USD"),
            "user_id": user_info.get("user_id", "N/A")  # Сохраняем UID
        })
    return table


def update_table(show_inactive):
    """Создает таблицу для отображения в Gradio."""
    users = load_data(show_inactive)
    formatted_rows = []

    for user in users:
        formatted_rows.append([
            user["username"],
            user["data_used"],
            user["data_limit"],
            user["status"],
            user["subscription_price"],
            user["user_id"],  # UID добавляем в таблицу
        ])

    return pd.DataFrame(
        formatted_rows,
        columns=["👤 User", "📊 Used", "📦 Limit", "⚡ St.", "💳 $", "UID"]
    )
