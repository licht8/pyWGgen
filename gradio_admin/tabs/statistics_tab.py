#!/usr/bin/env python3
# statistics_tab.py
# Вкладка "Statistics" Gradio-интерфейса wg_qr_generator

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


def get_user_info(user_id):
    """Возвращает подробную информацию о пользователе."""
    user_records = load_user_records()
    for user in user_records.values():
        if user.get("user_id") == user_id:
            return json.dumps(user, indent=4)
    return "User not found."


def block_user(user_id):
    """Блокирует пользователя."""
    user_records = load_user_records()
    for username, user in user_records.items():
        if user.get("user_id") == user_id:
            user["status"] = "blocked"
            with open(USER_DB_PATH, "w") as f:
                json.dump(user_records, f, indent=4)
            return f"User {username} blocked."
    return "User not found."


def delete_user(user_id):
    """Удаляет пользователя."""
    user_records = load_user_records()
    for username, user in list(user_records.items()):
        if user.get("user_id") == user_id:
            del user_records[username]
            with open(USER_DB_PATH, "w") as f:
                json.dump(user_records, f, indent=4)
            return f"User {username} deleted."
    return "User not found."


def statistics_tab():
    """Создает интерфейс вкладки статистики."""
    with gr.Tab("🔍 Statistics"):
        gr.Markdown("## Статистика пользователей")

        # Фильтры
        with gr.Row():
            search_box = gr.Textbox(label="Search", placeholder="Search for users...")
            show_inactive_checkbox = gr.Checkbox(label="Show inactive users", value=True)
            refresh_button = gr.Button("Refresh Table")

        # Таблица данных
        user_table = gr.Dataframe(prepare_table_data(), label="Users Table", interactive=False)

        # Подробная информация
        user_info_box = gr.Textbox(label="User Information", lines=10, interactive=False)

        # Управление пользователями
        with gr.Row():
            selected_user_id = gr.Textbox(label="Selected User ID", interactive=False)
            block_button = gr.Button("Block User")
            delete_button = gr.Button("Delete User")

        # Связывание компонентов
        def filter_table(search_query, show_inactive):
            df = prepare_table_data(show_inactive)
            if search_query:
                df = df[df.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
            return df

        refresh_button.click(lambda: prepare_table_data(), outputs=user_table)
        search_box.change(lambda q, show: filter_table(q, show), inputs=[search_box, show_inactive_checkbox], outputs=user_table)
        show_inactive_checkbox.change(lambda q, show: filter_table(q, show), inputs=[search_box, show_inactive_checkbox], outputs=user_table)
        user_table.select(lambda idx: get_user_info(user_table.value.iloc[idx]["UID"]), outputs=user_info_box)
        block_button.click(block_user, inputs=selected_user_id, outputs=user_info_box)
        delete_button.click(delete_user, inputs=selected_user_id, outputs=user_info_box)
