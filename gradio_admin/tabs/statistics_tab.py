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
            user.get("user_id", "N/A")  # UID для идентификации
        ])

    return pd.DataFrame(
        table,
        columns=["User", "Used", "Limit", "Status", "Price", "UID"]
    )


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

        # Поле поиска
        with gr.Row():
            search_input = gr.Textbox(label="Search", placeholder="Enter data to filter...")

        # Таблица пользователей (без UID)
        with gr.Row():
            user_table = gr.Dataframe(
                headers=["User", "Used", "Limit", "Status", "Price"],
                value=create_table(show_inactive=True).drop(columns=["UID"]),
                interactive=False,
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

        # Создание динамических кнопок для каждой строки
        def create_buttons():
            """Создает динамические кнопки для каждой строки таблицы."""
            buttons = []
            user_data = create_table()
            for _, row in user_data.iterrows():
                uid = row["UID"]

                def button_fn(uid=uid):
                    """Обертка для передачи UID в обработчик."""
                    return show_user_info(uid)

                # Добавляем кнопку
                buttons.append(
                    gr.Button(f"View User ({row['User'][:6]}...)")
                        .click(fn=button_fn, outputs=[selected_user_info])
                )
            return buttons

        # Отображение кнопок
        with gr.Row():
            button_container = gr.Column(create_buttons())
