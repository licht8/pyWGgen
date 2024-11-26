#!/usr/bin/env python3
# gradio_admin/functions/table_helpers.py
# Утилита для обработки и отображения данных в таблице Gradio

import json
import os

WG_USERS_JSON = "logs/wg_users.json"

def load_data(show_inactive=True):
    """Загружает данные пользователей из JSON."""
    if not os.path.exists(WG_USERS_JSON):
        return []

    with open(WG_USERS_JSON, "r") as f:
        users = json.load(f)

    table = []
    for username, user_info in users.items():
        if not show_inactive and user_info.get("status") != "active":
            continue
        table.append(user_info | {"username": username})
    return table

def update_table(show_inactive):
    """
    Форматирует данные таблицы с информацией о пользователях WireGuard.
    """
    users = load_data(show_inactive)
    formatted_rows = []

    for user in users:
        username = user.get("username", "N/A")
        public_key = user.get("public_key", "N/A")
        allowed_ips = user.get("allowed_ips", "N/A")
        last_handshake = user.get("last_handshake", "N/A")
        status = user.get("status", "inactive")
        status_color = "green" if status == "active" else "red"

        formatted_rows.append([
            username,
            public_key,
            allowed_ips,
            last_handshake,
            f"<span style='color: {status_color}'>{status}</span>"
        ])

    return formatted_rows
