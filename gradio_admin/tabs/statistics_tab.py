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
    df["Action"] = df["UID"].apply(lambda uid: f"View ({uid[:6]}...)")
    return df.drop(columns=["UID"])


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

        # Таблица с кнопками
        with gr.Row():
            user_table = gr.Dataframe(
                headers=["User", "Used", "Limit", "Status", "Price", "Action"],
                value=create_table_with_buttons(show_inactive=True),
                interactive=False,
            )

        # Обновление таблицы при изменении чекбокса
        def refresh_table(show_inactive):
            """Обновляет данные таблицы."""
            return create_table_with_buttons(show_inactive)

        refresh_button.click(
            fn=refresh_table,
            inputs=[show_inactive],
            outputs=[user_table]
        )

        # Отображение данных пользователя
        def show_user_info(action):
            """Показывает информацию о пользователе по выбранному действию."""
            uid = action.split()[1].strip("()")  # Извлекаем UID из кнопки
            user_records = load_user_records()
            user_info = next(
                (info for info in user_records.values() if info.get("user_id").startswith(uid)),
                None
            )
            if not user_info:
                return f"No user found with UID: {uid}"
            return json.dumps(user_info, indent=4, ensure_ascii=False)

        # Выбор строки через таблицу
        user_table.select(
            fn=show_user_info,
            inputs=[user_table],
            outputs=[selected_user_info]
        )
