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


def create_table(show_inactive=True):
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
            user.get("user_id", "N/A")  # UID для передачи через кнопку
        ])

    df = pd.DataFrame(
        table,
        columns=["User", "Used", "Limit", "Status", "Price", "UID"]
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
            refresh_button = gr.Button("Refresh Table")

        # Область для отображения информации о выбранном пользователе
        with gr.Row():
            selected_user_info = gr.Textbox(
                label="User Information",
                interactive=False,
                value="Use the 'View' button to select a user.",
            )

        # Кнопки действий
        with gr.Row():
            block_button = gr.Button("Block User")
            delete_button = gr.Button("Delete User")

        # Таблица пользователей
        with gr.Row():
            user_table = gr.Dataframe(
                headers=["User", "Used", "Limit", "Status", "Price"],
                value=create_table(show_inactive=True).drop(columns=["UID"]),
                interactive=False,  # Таблица только для чтения
            )

        # Функция обновления таблицы
        def refresh_table(show_inactive):
            """Обновляет данные таблицы в зависимости от чекбокса."""
            return create_table(show_inactive).drop(columns=["UID"])

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

        # Функция для создания списка кнопок с UID
        def create_buttons(data):
            """Создает кнопки для каждой строки с привязкой UID."""
            buttons = []
            for uid in data["UID"]:
                buttons.append(gr.Button(f"View User ({uid[:6]}...)"))
            return buttons

        # Таблица с кнопками
        with gr.Row():
            table_buttons = gr.Column(create_buttons(create_table()))

        # Привязка кнопок к обработчику
        def bind_buttons():
            """Привязывает каждую кнопку к UID."""
            for i, uid in enumerate(create_table()["UID"]):
                table_buttons[i].click(
                    fn=show_user_info,
                    inputs=[uid],
                    outputs=[selected_user_info]
                )

        bind_buttons()
