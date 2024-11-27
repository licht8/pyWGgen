#!/usr/bin/env python3
# statistics_tab.py
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


def create_table_with_buttons(show_inactive=True):
    """Создает таблицу с кнопками для взаимодействия."""
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
            user.get("user_id", "N/A"),  # UID для передачи
        ])

    # Создаем DataFrame с колонкой кнопок
    df = pd.DataFrame(
        table,
        columns=["User", "Used", "Limit", "Status", "Price", "UID"]
    )

    # Добавляем кнопки в таблицу
    return df


def statistics_tab():
    """Создает вкладку статистики."""
    with gr.Tab("🔍 Statistics"):
        with gr.Row():
            gr.Markdown("## User Statistics")

        # Чекбокс для показа/скрытия неактивных пользователей
        with gr.Row():
            show_inactive = gr.Checkbox(label="Show inactive users", value=True)
            refresh_button = gr.Button("Refresh Table")

        # Область для отображения информации о выбранном пользователе
        with gr.Row():
            selected_user_info = gr.Textbox(
                label="User Information",
                interactive=False,
                value="Click 'View' to see user details.",
            )

        # Основная таблица с кнопками
        def generate_table_with_buttons(show_inactive):
            """Создает HTML-таблицу с кнопками."""
            df = create_table_with_buttons(show_inactive)
            df["Action"] = df["UID"].apply(
                lambda uid: f"<button class='gr-button' onclick=\"setUID('{uid}')\">View</button>"
            )
            table_html = df.drop(columns=["UID"]).to_html(
                escape=False,
                index=False,
                classes="gr-table"
            )
            return table_html

        with gr.Row():
            user_table = gr.HTML(value=generate_table_with_buttons(show_inactive=True))

        # Обновление таблицы
        refresh_button.click(
            fn=generate_table_with_buttons,
            inputs=[show_inactive],
            outputs=[user_table]
        )

        # Передача UID через JavaScript
        gr.HTML("""
        <script>
        function setUID(uid) {
            const textbox = document.querySelector('textarea[aria-label="selected_user_info"]');
            textbox.value = uid;
            textbox.dispatchEvent(new Event('input'));
        }
        </script>
        """)

        # Функция отображения информации о пользователе
        def show_user_info(uid):
            """Показывает информацию о пользователе по UID."""
            user_records = load_user_records()
            user_info = next(
                (info for info in user_records.values() if info.get("user_id") == uid),
                None
            )
            if not user_info:
                return f"No user found with UID: {uid}"
            return json.dumps(user_info, indent=4, ensure_ascii=False)

        # Скрытое поле для передачи UID
        selected_uid = gr.Textbox(visible=False)

        selected_uid.change(
            fn=show_user_info,
            inputs=[selected_uid],
            outputs=[selected_user_info]
        )
