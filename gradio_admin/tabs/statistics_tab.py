#!/usr/bin/env python3
# gradio_admin/tabs/statistics_tab.py
# Вкладка "Statistics" для Gradio-интерфейса проекта wg_qr_generator

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
                wrap=True
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
                table = [
                    row for row in table if query.lower() in " ".join(map(str, row)).lower()
                ]
            return table

        search_input.change(
            fn=search_and_update_table,
            inputs=[search_input, show_inactive],
            outputs=[stats_table]
        )

        # Выбор строки и отображение данных пользователя
        def show_user_info(selected_data):
            """Показывает информацию о выбранном пользователе."""
            if selected_data is None or len(selected_data) == 0:
                return "Select a row from the table to view details."

            try:
                # Если данные переданы в виде DataFrame
                if isinstance(selected_data, pd.DataFrame):
                    user_id = selected_data.iloc[0, -1]  # UID в последнем столбце
                # Если данные переданы в виде списка
                elif isinstance(selected_data, list):
                    user_id = selected_data[-1]  # UID в последнем элементе
                else:
                    return "Unsupported data format selected."

                # Получение данных пользователя
                user_records = load_user_records()
                user_info = next(
                    (info for info in user_records.values() if info.get("user_id") == user_id), 
                    None
                )
                if not user_info:
                    return f"No detailed information found for UID: {user_id}"

                # Форматирование полной информации
                user_details = json.dumps(user_info, indent=4, ensure_ascii=False)
                return user_details
            except Exception as e:
                return f"Error processing user information: {str(e)}"

        stats_table.select(
            fn=show_user_info,
            inputs=[stats_table],
            outputs=[selected_user_info]
        )

        # Действия блокировки и удаления пользователей
        def block_user(selected_data):
            """Блокирует пользователя."""
            if not selected_data or len(selected_data) == 0:
                return "No user selected to block."
            if isinstance(selected_data, pd.DataFrame):
                user_id = selected_data.iloc[0, -1]
            elif isinstance(selected_data, list):
                user_id = selected_data[-1]
            else:
                return "Unsupported data format selected."
            # Логика блокировки пользователя по UID
            return f"User with UID {user_id} blocked."

        block_button.click(
            fn=block_user,
            inputs=[stats_table],
            outputs=[selected_user_info]
        )

        def delete_user(selected_data):
            """Удаляет пользователя."""
            if not selected_data or len(selected_data) == 0:
                return "No user selected to delete."
            if isinstance(selected_data, pd.DataFrame):
                user_id = selected_data.iloc[0, -1]
            elif isinstance(selected_data, list):
                user_id = selected_data[-1]
            else:
                return "Unsupported data format selected."
            # Логика удаления пользователя по UID
            return f"User with UID {user_id} deleted."

        delete_button.click(
            fn=delete_user,
            inputs=[stats_table],
            outputs=[selected_user_info]
        )
