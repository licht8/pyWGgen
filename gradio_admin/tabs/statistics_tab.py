#!/usr/bin/env python3
# statistics_tab.py
# Болванка для вкладки "Statistics" Gradio-интерфейса wg_qr_generator

import gradio as gr
import pandas as pd
import json
import os
from settings import USER_DB_PATH  # Путь к JSON с данными пользователей


def load_user_records():
    """Загружает данные пользователей из JSON."""
    if not os.path.exists(USER_DB_PATH):
        return {}

    with open(USER_DB_PATH, "r") as f:
        return json.load(f)


def prepare_table_data(show_inactive=True):
    """Создает данные для таблицы."""
    user_records = load_user_records()
    table_data = []

    for user in user_records.values():
        if not show_inactive and user.get("status") != "active":
            continue
        table_data.append([
            user.get("username", "N/A"),
            user.get("data_used", "0.0 KiB"),
            user.get("data_limit", "100.0 GB"),
            user.get("status", "inactive"),
            user.get("subscription_price", "0.00 USD"),
            user.get("user_id", "N/A")
        ])

    return pd.DataFrame(table_data, columns=["User", "Used", "Limit", "Status", "Price", "UID"])


def statistics_tab():
    """Создает болванку вкладки статистики."""
    with gr.Tab("🔍 Statistics"):
        gr.Markdown("""
        # Тут начинается интерфейс вкладки "Статистика"

        ## Здесь будет реализован функционал статистики

        # Тут заканчивается интерфейс вкладки
        """)
