#!/usr/bin/env python3
# statistics_tab.py
# Вкладка "Statistics" с базовой информацией о пользователях

import gradio as gr
import json
import os
from settings import USER_DB_PATH  # Путь к JSON с данными пользователей


def load_user_records():
    """Загружает данные пользователей из JSON."""
    if not os.path.exists(USER_DB_PATH):
        return {}
    with open(USER_DB_PATH, "r") as f:
        return json.load(f)


def prepare_user_list(show_inactive):
    """Подготавливает список пользователей для отображения."""
    user_records = load_user_records()
    users = []
    for user in user_records.values():
        if not show_inactive and user.get("status") != "active":
            continue
        users.append(f"{user['username']} ({user['user_id']})")
    return users


def get_user_info(selected_user):
    """Возвращает информацию о выбранном пользователе."""
    if not selected_user:
        return "Выберите пользователя из списка, чтобы увидеть информацию."
    user_id = selected_user.split("(")[-1].strip(")")
    user_records = load_user_records()
    for user in user_records.values():
        if user.get("user_id") == user_id:
            return (
                f"### Информация о пользователе: {user['username']}\n\n"
                f"- **ID:** {user['user_id']}\n"
                f"- **Статус:** {user.get('status', 'N/A')}\n"
                f"- **Использование данных:** {user.get('data_used', '0.0 KiB')} / {user.get('data_limit', '100.0 GB')}\n"
                f"- **План подписки:** {user.get('subscription_plan', 'N/A')}\n"
                f"- **Цена:** {user.get('subscription_price', '0.00 USD')}\n"
                f"- **Последнее обновление:** {user.get('last_config_update', 'N/A')}\n"
            )
    return "Пользователь не найден."


def statistics_tab():
    """Создает вкладку 'Statistics'."""
    with gr.Tab("🔍 Statistics"):
        gr.Markdown("## Список пользователей WireGuard")

        # Фильтр и кнопка обновления
        with gr.Row():
            show_inactive_checkbox = gr.Checkbox(label="Show inactive users", value=True)
            refresh_button = gr.Button("Refresh")

        # Выпадающий список пользователей
        user_dropdown = gr.Dropdown(
            label="Выберите пользователя",
            choices=[],
            interactive=True,
        )

        # Информация о выбранном пользователе
        user_info_box = gr.Markdown("Выберите пользователя из списка, чтобы увидеть информацию.")

        # Логика обновления списка пользователей
        def update_user_list(show_inactive):
            users = prepare_user_list(show_inactive)
            return gr.Dropdown.update(choices=users, value=None)

        # Обновление информации о пользователе
        user_dropdown.change(
            fn=get_user_info,
            inputs=[user_dropdown],
            outputs=user_info_box,
        )

        # Обновление списка пользователей
        refresh_button.click(
            fn=update_user_list,
            inputs=[show_inactive_checkbox],
            outputs=[user_dropdown],
        )

        # Инициализация списка при загрузке
        refresh_button.click(
            fn=update_user_list,
            inputs=[show_inactive_checkbox],
            outputs=[user_dropdown],
            queue=False,
        )
