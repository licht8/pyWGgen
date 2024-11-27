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


def update_table_with_buttons(show_inactive=True):
    """Создает таблицу с кнопками для отображения в Gradio."""
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

    df = pd.DataFrame(
        table,
        columns=["👤 User", "📊 Used", "📦 Limit", "⚡ St.", "💳 $", "UID"]
    )

    # Добавляем кнопки в таблицу
    df["Action"] = df["UID"].apply(
        lambda uid: f"<button class='select-button' onclick='setUserID(\"{uid}\")'>Select</button>"
    )
    return df


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
                value="Use the 'Select' button in the table to view user details.",
            )

        # Кнопки действий
        with gr.Row():
            block_button = gr.Button("Block User")
            delete_button = gr.Button("Delete User")

        # Поле поиска
        with gr.Row():
            search_input = gr.Textbox(label="Search", placeholder="Enter data to filter...")

        # Таблица с кнопками
        with gr.Row():
            stats_table = gr.HTML(value=update_table_with_buttons(show_inactive=True).to_html(escape=False, index=False))

        # Функция обновления таблицы
        def refresh_table(show_inactive):
            """Обновляет данные таблицы в зависимости от чекбокса."""
            df = update_table_with_buttons(show_inactive)
            return df.to_html(escape=False, index=False)

        refresh_button.click(
            fn=refresh_table,
            inputs=[show_inactive],
            outputs=[stats_table]
        )

        # Поиск и обновление таблицы
        def search_and_update_table(query, show_inactive):
            """Фильтрует данные таблицы по запросу в поиске."""
            table = update_table_with_buttons(show_inactive)
            if query.strip():
                table = table[table.apply(
                    lambda row: query.lower() in row.to_string().lower(), axis=1
                )]
            return table.to_html(escape=False, index=False)

        search_input.change(
            fn=search_and_update_table,
            inputs=[search_input, show_inactive],
            outputs=[stats_table]
        )

        # Получение информации о пользователе через кнопку
        def show_user_info_by_uid(uid):
            """Показывает информацию о пользователе по UID."""
            user_records = load_user_records()
            user_info = next(
                (info for info in user_records.values() if info.get("user_id") == uid),
                None
            )

            if not user_info:
                return f"No detailed information found for UID: {uid}"

            user_details = json.dumps(user_info, indent=4, ensure_ascii=False)
            return user_details

        # Кнопка для получения данных о пользователе
        stats_table.change(
            fn=show_user_info_by_uid,
            inputs=[stats_table],
            outputs=[selected_user_info]
        )
