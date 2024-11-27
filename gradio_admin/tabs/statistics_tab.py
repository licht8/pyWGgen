#!/usr/bin/env python3
# statistics_tab.py
# Полностью переработанная вкладка "Statistics" для Gradio-интерфейса wg_qr_generator

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
    """Создает вкладку статистики."""
    with gr.Tab("🔍 Statistics"):
        with gr.Row():
            gr.Markdown("## User Statistics")

        # Чекбокс для показа/скрытия неактивных пользователей
        with gr.Row():
            show_inactive = gr.Checkbox(label="Show inactive users", value=True)
            refresh_button = gr.Button("Refresh Table")

        # Поле поиска
        with gr.Row():
            search_input = gr.Textbox(label="Search", placeholder="Enter text to filter...")

        # Основная таблица
        user_table = gr.Dataframe(
            headers=["User", "Used", "Limit", "Status", "Price", "Action"],
            interactive=False,
            label="User Table"
        )

        # Область для отображения информации о пользователе
        with gr.Row():
            user_info_display = gr.Textbox(
                label="User Information",
                interactive=False,
                value="Select a user or click 'View' to see details."
            )

        # Функция обновления таблицы
        def update_table(show_inactive, search_query):
            """Обновляет таблицу в зависимости от фильтров."""
            df = prepare_table_data(show_inactive)
            if search_query.strip():
                df = df[df.apply(
                    lambda row: search_query.lower() in row.to_string().lower(), axis=1
                )]
            # Добавляем колонку кнопок
            df["Action"] = df["UID"].apply(lambda uid: f"<button onclick=\"selectUser('{uid}')\">View</button>")
            return df.drop(columns=["UID"])

        # Функция отображения информации о пользователе
        def show_user_info(uid):
            """Показывает информацию о пользователе по UID."""
            user_records = load_user_records()
            user_info = next(
                (info for info in user_records.values() if info.get("user_id") == uid),
                None
            )
            if not user_info:
                print(f"[DEBUG] User with UID {uid} not found.")  # Отладочная информация
                return f"No user found with UID: {uid}"
            print(f"[DEBUG] Displaying info for user UID {uid}: {user_info}")  # Отладочная информация
            return json.dumps(user_info, indent=4, ensure_ascii=False)

        # Передача UID через JavaScript
        gr.HTML("""
        <script>
        function selectUser(uid) {
            const textbox = document.querySelector('textarea[aria-label="selected_uid"]');
            textbox.value = uid;
            textbox.dispatchEvent(new Event('input'));
        }
        </script>
        """)

        # Скрытое поле для передачи UID
        selected_uid = gr.Textbox(visible=False)

        selected_uid.change(
            fn=show_user_info,
            inputs=[selected_uid],
            outputs=[user_info_display]
        )

        # Привязка кнопки "Refresh Table"
        refresh_button.click(
            fn=update_table,
            inputs=[show_inactive, search_input],
            outputs=[user_table]
        )

        # Начальная загрузка таблицы
        user_table.value = update_table(show_inactive=True, search_query="")
