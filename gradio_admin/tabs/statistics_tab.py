#!/usr/bin/env python3
# gradio_admin/tabs/statistics_tab.py

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


def update_table(show_inactive=True):
    """Создает таблицу для отображения в Gradio."""
    user_records = load_user_records()
    table = []

    for user in user_records.values():
        if not show_inactive and user.get("status") != "active":
            continue
        table.append([
            user.get("username", "N/A"),
            user.get("data_used", "0.0 KiB"),
            user.get("data_limit", "100.0 GB"),
            user.get("status", "inactive"),
            user.get("subscription_price", "0.00 USD"),
            user.get("user_id", "N/A")  # Добавляем user_id для идентификации
        ])

    return pd.DataFrame(
        table,
        columns=["👤 User", "📊 Used", "📦 Limit", "⚡ St.", "💳 $", "UID"]
    )


def statistics_tab():
    """Возвращает вкладку статистики пользователей WireGuard."""
    with gr.Tab("🔍 Statistics"):
        with gr.Row():
            gr.Markdown("## User Statistics")

        # Чекбокс Show inactive и кнопка Refresh
        with gr.Row():
            show_inactive = gr.Checkbox(label="Show inactive", value=True)
            refresh_button = gr.Button("Refresh")

        # Область для отображения информации о выбранном пользователе
        with gr.Row():
            selected_user_info = gr.Textbox(
                label="User Information",
                interactive=False,
                value="Select a user to view details.",
            )

        # Кнопки действий
        with gr.Row():
            block_button = gr.Button("Block User")
            delete_button = gr.Button("Delete User")

        # Поле поиска
        with gr.Row():
            search_input = gr.Textbox(label="Search", placeholder="Enter data to filter...")

        # Таблица с данными
        with gr.Row():
            stats_table = gr.Dataframe(
                headers=["👤 User", "📊 Used", "📦 Limit", "⚡ St.", "💳 $", "UID"],
                value=update_table(show_inactive=True),
                interactive=False,  # Таблица только для чтения
            )

        # Функция обновления таблицы
        def refresh_table(show_inactive):
            """Обновляет данные таблицы в зависимости от чекбокса."""
            return update_table(show_inactive)

        refresh_button.click(
            fn=refresh_table,
            inputs=[show_inactive],
            outputs=[stats_table]
        )

        # Поиск и обновление таблицы
        def search_and_update_table(query, show_inactive):
            """Фильтрует данные таблицы по запросу в поиске."""
            table = update_table(show_inactive)
            if query.strip():
                table = table[table.apply(
                    lambda row: query.lower() in row.to_string().lower(), axis=1
                )]
            return table

        search_input.change(
            fn=search_and_update_table,
            inputs=[search_input, show_inactive],
            outputs=[stats_table]
        )

        # Выбор строки и отображение данных пользователя
        def show_user_info(selected_data):
            """Показывает информацию о выбранном пользователе."""
            if selected_data is None or (isinstance(selected_data, pd.DataFrame) and selected_data.empty):
                return "Select a row from the table to view details."

            try:
                # Проверяем формат данных
                if isinstance(selected_data, list):
                    # UID находится в последнем элементе строки
                    user_id = selected_data[-1]
                elif isinstance(selected_data, pd.DataFrame):
                    user_id = selected_data.iloc[0, -1]  # UID в последнем столбце DataFrame
                else:
                    return "[ERROR] Unsupported data format selected."

                # Логируем выбор
                print(f"Selected User ID: {user_id}")

                # Поиск информации о пользователе
                user_records = load_user_records()
                user_info = next(
                    (info for info in user_records.values() if info.get("user_id") == user_id),
                    None
                )

                if not user_info:
                    return f"No detailed information found for UID: {user_id}"

                # Форматирование данных для вывода
                user_details = json.dumps(user_info, indent=4, ensure_ascii=False)
                return user_details
            except Exception as e:
                return f"Error processing user information: {str(e)}"

        stats_table.select(
            fn=show_user_info,
            inputs=[stats_table],
            outputs=[selected_user_info]
        )
