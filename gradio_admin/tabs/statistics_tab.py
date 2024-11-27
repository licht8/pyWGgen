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

        # Таблица с данными
        with gr.Row():
            stats_table = gr.Dataframe(
                headers=["👤 User", "📊 Used", "📦 Limit", "⚡ St.", "💳 $", "UID"],
                value=update_table(show_inactive=True),
                interactive=False,  # Таблица только для чтения
                elem_id="stats-table",  # ID для JavaScript
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

        # Функция для отображения информации о пользователе
        def show_user_info(user_id):
            """Показывает информацию о выбранном пользователе."""
            user_records = load_user_records()
            user_info = next(
                (info for info in user_records.values() if info.get("user_id") == user_id), 
                None
            )
            if not user_info:
                return f"No detailed information found for UID: {user_id}"

            return json.dumps(user_info, indent=4, ensure_ascii=False)

        # Скрипт для обработки кликов
        with gr.Row():
            gr.Markdown(
                """
                <script>
                document.addEventListener("DOMContentLoaded", function() {
                    const table = document.querySelector("#stats-table");
                    table.addEventListener("click", function(event) {
                        const row = event.target.closest("tr");
                        if (row) {
                            const uid = row.querySelector("td:last-child").innerText;
                            console.log("Selected UID:", uid);
                            const userIdInput = document.querySelector("#user-id-input");
                            userIdInput.value = uid;
                            userIdInput.dispatchEvent(new Event("input", { bubbles: true }));
                        }
                    });
                });
                </script>
                """, 
                elem_id="js-handler"
            )

        # Скрытый компонент для передачи user_id
        user_id_input = gr.Textbox(
            label="Hidden UID",
            elem_id="user-id-input",
            visible=False
        )

        # Отслеживание изменений в `user_id_input`
        user_id_input.change(
            fn=show_user_info,
            inputs=[user_id_input],
            outputs=[selected_user_info]
        )
