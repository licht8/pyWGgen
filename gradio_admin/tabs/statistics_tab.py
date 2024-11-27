#!/usr/bin/env python3
# statistics_tab.py
# Полностью обновленная вкладка "Statistics" для Gradio-интерфейса wg_qr_generator

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
        table_data.append({
            "User": user.get("username", "N/A"),
            "Used": user.get("data_used", "0.0 KiB"),
            "Limit": user.get("data_limit", "100.0 GB"),
            "Status": user.get("status", "inactive"),
            "Price": user.get("subscription_price", "0.00 USD"),
            "UID": user.get("user_id", "N/A")
        })

    return pd.DataFrame(table_data)


def statistics_tab():
    """Создает вкладку статистики."""
    with gr.Tab("🔍 Statistics"):
        with gr.Row():
            gr.Markdown("## User Statistics")

        # Чекбокс для фильтрации активных пользователей
        with gr.Row():
            show_inactive = gr.Checkbox(label="Show inactive users", value=True)
            refresh_button = gr.Button("Refresh Table")

        # Поле поиска
        with gr.Row():
            search_input = gr.Textbox(label="Search", placeholder="Enter text to filter...")

        # Таблица пользователей
        user_table = gr.Dataframe(
            headers=["User", "Used", "Limit", "Status", "Price", "UID", "Action"],
            interactive=False
        )

        # Область для отображения информации о пользователе
        with gr.Row():
            user_info_display = gr.Textbox(
                label="User Information",
                interactive=False,
                value="Select a user to view their details."
            )

        # Кнопки управления пользователями
        with gr.Row():
            block_button = gr.Button("Block User")
            delete_button = gr.Button("Delete User")

        # Функция обновления таблицы
        def update_table(show_inactive, search_query):
            """Обновляет таблицу в зависимости от фильтров."""
            df = prepare_table_data(show_inactive)
            if search_query.strip():
                df = df[df.apply(
                    lambda row: search_query.lower() in row.to_string().lower(), axis=1
                )]
            df["Action"] = df["UID"].apply(lambda uid: f"View ({uid[:6]}...)")
            return df.drop(columns=["UID"])

        # Функция отображения информации о пользователе
        def show_user_info(action):
            """Показывает информацию о пользователе по UID."""
            uid = action.split()[1].strip("()")
            user_records = load_user_records()
            user_info = next(
                (info for info in user_records.values() if info.get("user_id") == uid),
                None
            )
            if not user_info:
                return f"No user found with UID: {uid}"
            return json.dumps(user_info, indent=4, ensure_ascii=False)

        # Функция блокировки пользователя
        def block_user(action):
            """Блокирует выбранного пользователя."""
            uid = action.split()[1].strip("()")
            user_records = load_user_records()
            user = next(
                (info for info in user_records.values() if info.get("user_id") == uid),
                None
            )
            if not user:
                return "User not found."
            user["status"] = "blocked"
            with open(USER_DB_PATH, "w") as f:
                json.dump(user_records, f, indent=4)
            return f"User {user.get('username', 'N/A')} has been blocked."

        # Привязка функций к кнопкам
        refresh_button.click(
            fn=lambda show_inactive, search_query: update_table(show_inactive, search_query),
            inputs=[show_inactive, search_input],
            outputs=[user_table]
        )

        user_table.select(
            fn=show_user_info,
            inputs=[user_table],
            outputs=[user_info_display]
        )

        block_button.click(
            fn=block_user,
            inputs=[user_table],
            outputs=[user_info_display]
        )

        delete_button.click(
            fn=lambda action: f"Delete user with UID: {action.split()[1].strip('()')}",
            inputs=[user_table],
            outputs=[user_info_display]
        )
