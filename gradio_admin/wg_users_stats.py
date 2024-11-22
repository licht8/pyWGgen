#!/usr/bin/env python3
# gradio_admin/wg_users_stats.py
"""
Функции для получения статистики пользователей WireGuard.
"""

import json

JSON_LOG_PATH = "/var/log/wg_users.json"

def load_data(show_inactive):
    """
    Загружает данные пользователей WireGuard из JSON-файла и фильтрует их.
    
    :param show_inactive: Флаг, показывать ли неактивных пользователей.
    :return: Отформатированный список данных для отображения.
    """
    try:
        with open(JSON_LOG_PATH, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        return [["Нет данных о пользователях"]]

    users = data.get("users", {})
    table = []

    for username, user_data in users.items():
        if not show_inactive and user_data["status"] == "inactive":
            continue
        table.append([
            username,
            ", ".join(user_data["endpoints"]),
            user_data["allowed_ips"],
            user_data["total_transfer"]["received"],
            user_data["total_transfer"]["sent"],
            user_data["last_handshake"] or "Никогда",
            "Активен" if user_data["status"] == "active" else "Неактивен"
        ])

    return table
