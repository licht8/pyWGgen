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


def create_html_table(show_inactive=True):
    """Создает HTML-таблицу с кнопками для отображения в Gradio."""
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
            user.get("user_id", "N/A")  # UID для передачи через кнопку
        ])

    df = pd.DataFrame(
        table,
        columns=["User", "Used", "Limit", "Status", "Price", "UID"]
    )

    # Генерация HTML с кнопками
    def row_to_html(row):
        return f"""
        <tr>
            <td>{row['User']}</td>
            <td>{row['Used']}</td>
            <td>{row['Limit']}</td>
            <td>{row['Status']}</td>
            <td>{row['Price']}</td>
            <td>
                <button onclick="setUserID('{row['UID']}')" class="btn btn-sm">View</button>
            </td>
        </tr>
        """

    rows_html = "\n".join(df.apply(row_to_html, axis=1))
    return f"""
    <table class="gr-table">
        <thead>
            <tr>
                <th>User</th>
                <th>Used</th>
                <th>Limit</th>
                <th>Status</th>
                <th>Price</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """


def statistics_tab():
    """Возвращает вкладку статистики пользователей WireGuard."""
    with gr.Tab("🔍 Statistics"):
        with gr.Row():
            gr.Markdown("## User Statistics")

        # Чекбокс Show inactive и кнопка Refresh
        with gr.Row():
            show_inactive = gr.Checkbox(label="Show inactive", value=True)
            refresh_button = gr.Button("Refresh Table")

        # Область для отображения информации о выбранном пользователе
        with gr.Row():
            selected_user_info = gr.Textbox(
                label="User Information",
                interactive=False,
                value="Use the 'View' button in the table to select a user.",
            )

        # Таблица с пользователями
        with gr.Row():
            user_table = gr.HTML(value=create_html_table(show_inactive=True))

        # Функция обновления таблицы
        def refresh_table(show_inactive):
            """Обновляет данные таблицы."""
            return create_html_table(show_inactive)

        refresh_button.click(
            fn=refresh_table,
            inputs=[show_inactive],
            outputs=[user_table]
        )

        # Функция отображения информации о пользователе
        def show_user_info(uid):
            """Отображает информацию о пользователе по UID."""
            user_records = load_user_records()
            user_info = next(
                (info for info in user_records.values() if info.get("user_id") == uid),
                None
            )
            if not user_info:
                return f"No user found with UID: {uid}"
            return json.dumps(user_info, indent=4, ensure_ascii=False)

        # Передача UID через кнопку
        with gr.Row():
            selected_uid = gr.Textbox(visible=False)

        selected_uid.change(
            fn=show_user_info,
            inputs=[selected_uid],
            outputs=[selected_user_info]
        )

        # Встраиваем JavaScript для передачи UID в скрытое поле
        gr.HTML("""
        <script>
        function setUserID(uid) {
            document.querySelector('textarea[aria-label="selected_uid"]').value = uid;
            document.querySelector('textarea[aria-label="selected_uid"]').dispatchEvent(new Event('input'));
        }
        </script>
        """)
