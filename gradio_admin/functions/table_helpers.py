#!/usr/bin/env python3
# gradio_admin/functions/table_helpers.py

import os
import json
import pandas as pd # type: ignore
from settings import USER_DB_PATH  # Путь к JSON с данными пользователей

def load_data(show_inactive=True):
    """Loads user data from JSON."""
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
            "allowed_ips": user_info.get("allowed_ips", "N/A"),  # Adding IP address
            "status": user_info.get("status", "inactive"),
            "subscription_price": user_info.get("subscription_price", "0.00 USD"),
            "user_id": user_info.get("user_id", "N/A")  # UID added
        })
    return table


def update_table(show_inactive):
    """Creates a table for display in Gradio."""
    users = load_data(show_inactive)
    formatted_rows = []

    for user in users:
        formatted_rows.append([
            user["username"],
            user["data_used"],
            user["data_limit"],
            user["allowed_ips"],  # Including IP address after data_limit
            user["status"],
            user["subscription_price"],
            user["user_id"]  # UID
        ])

    return pd.DataFrame(
        formatted_rows,
        columns=["👤 User", "📊 Used", "📦 Limit", "🌐 IP Address", "⚡ St.", "💳 $", "UID"]  # Updated headers
    )