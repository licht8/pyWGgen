#!/usr/bin/env python3
# gradio_admin/functions/table_helpers.py

import os
import json
import pandas as pd  # type: ignore
from settings import USER_DB_PATH  # Ścieżka do pliku JSON z danymi użytkowników

def load_data(show_inactive=True):
    """Wczytuje dane użytkowników z JSON."""
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
            "total_transfer": user_info.get("total_transfer", "0.0 KiB"),
            "data_limit": user_info.get("data_limit", "100.0 GB"),
            "allowed_ips": user_info.get("allowed_ips", "N/A"),  # Dodanie adresu IP
            "status": user_info.get("status", "inactive"),
            "subscription_price": user_info.get("subscription_price", "0.00 USD"),
            "user_id": user_info.get("user_id", "N/A")  # Dodano UID
        })
    return table

def update_table(show_inactive):
    """Tworzy tabelę do wyświetlenia w Gradio."""
    users = load_data(show_inactive)
    formatted_rows = []

    for user in users:
        formatted_rows.append([
            user["username"],
            user["total_transfer"],
            user["data_limit"],
            user["allowed_ips"],  # IP po limicie danych
            user["status"],
            user["subscription_price"],
            user["user_id"]  # UID
        ])

    return pd.DataFrame(
        formatted_rows,
        columns=["👤 Użytkownik", "📊 Zużyto", "📦 Limit", "🌐 Adres IP", "⚡ Stan", "💳 Cena", "UID"]  # Zaktualizowane nagłówki
    )
