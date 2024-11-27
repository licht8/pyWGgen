#!/usr/bin/env python3
# gradio_admin/tabs/statistics_tab.py
# Вкладка "Statistics" для Gradio-интерфейса проекта wg_qr_generator

import gradio as gr
import pandas as pd
import json
import os
from gradio_admin.functions.table_helpers import update_table
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

        # Поле поиска
        with gr.Row():
            search_input = gr.Textbox(label="Search", placeholder="Enter data to filter...")

        # Таблица с данными
        with gr.Row():
            stats_table = gr.Dataframe(
                headers=["👤 User", "📊 Used", "📦 Limit", "⚡ St.", "💳 $"],
                value=update_table(show_inactive=True),
                interactive=False,  # Таблица только для чтения
                wrap=True
            )

        # Обновление таблицы
        def refresh_table(show_inactive):
            """Обновляет данные таблицы."""
            return update_table(show_inactive)

        refresh_button.click(
            fn=refresh_table,
            inputs=[show_inactive],
            outputs=[stats_table]
        )

        # Поиск и обновление таблицы
        def search_and_update_table(query, show_inactive):
            """Фильтрует данные таблицы по запросу."""
            table = update_table(show_inactive)
            if query:
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
            if selected_data is None:
                return "Select a row from the table to view details."
            
            username = selected_data[0]  # Первое поле — имя пользователя
            user_records = load_user_records()
            user_info = user_records.get(username, {})
            if not user_info:
                return "No detailed information found for this user."

            # Форматирование информации с эмодзи
            details = [
                f"👤 **Username**: {user_info.get('username', 'N/A')}",
                f"📧 **Email**: {user_info.get('email', 'N/A')}",
                f"📱 **Telegram**: {user_info.get('telegram_id', 'N/A')}",
                f"🔗 **Allowed IPs**: {user_info.get('allowed_ips', 'N/A')}",
                f"📊 **Data Used**: {user_info.get('data_used', '0.0 KiB')}",
                f"📦 **Data Limit**: {user_info.get('data_limit', '100.0 GB')}",
                f"⚡ **Status**: {user_info.get('status', 'inactive')}",
                f"💳 **Subscription Plan**: {user_info.get('subscription_plan', 'free')}",
                f"🛠️ **Public Key**: {user_info.get('public_key', 'N/A')}",
                f"🔑 **Preshared Key**: {user_info.get('preshared_key', 'N/A')}",
            ]
            return "\n".join(details)

        stats_table.select(
            fn=show_user_info,
            inputs=[stats_table],
            outputs=[selected_user_info]
        )
