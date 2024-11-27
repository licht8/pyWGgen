#!/usr/bin/env python3
# statistics_tab.py
# Вкладка "Statistics" Gradio-интерфейса wg_qr_generator

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


def prepare_user_choices(show_inactive=True):
    """Создает список пользователей для Dropdown."""
    user_records = load_user_records()
    user_choices = []
    for user in user_records.values():
        if not show_inactive and user.get("status") != "active":
            continue
        user_choices.append(f"{user['username']} ({user['user_id']})")
    return user_choices


def get_user_info(selected_user):
    """Возвращает подробную информацию о пользователе."""
    if not selected_user:
        return (
            "Начните вводить имя пользователя или выберите его из списка ниже. "
            "После выбора вы сможете увидеть информацию о пользователе и выполнить действия."
        )
    
    user_id = selected_user.split("(")[-1].strip(")")
    user_records = load_user_records()
    for user in user_records.values():
        if user.get("user_id") == user_id:
            return json.dumps(user, indent=4)
    return "Пользователь не найден."


def dummy_action(selected_user):
    """Заглушка для кнопок действий."""
    if not selected_user:
        return "Сначала выберите пользователя."
    return f"Действие выполнено для пользователя: {selected_user}"


def statistics_tab():
    """Создает интерфейс вкладки статистики."""
    with gr.Tab("🔍 Statistics"):
        gr.Markdown("## Управление пользователями WireGuard")

        # Верхний блок с фильтром и кнопкой обновления
        with gr.Row():
            show_inactive_checkbox = gr.Checkbox(label="Show inactive users", value=True)
            refresh_button = gr.Button("Refresh")

        # Поле информации о пользователе
        user_info_box = gr.Textbox(
            label="Информация о пользователе",
            lines=10,
            interactive=False,
            value=(
                "Начните вводить имя пользователя или выберите его из списка ниже. "
                "После выбора вы сможете увидеть информацию о пользователе и выполнить действия."
            )
        )

        # Блок кнопок действий
        with gr.Row():
            block_button = gr.Button("Block")
            delete_button = gr.Button("Delete")
            archive_button = gr.Button("Archive")

        # Выпадающее меню выбора пользователя
        user_dropdown = gr.Dropdown(
            choices=prepare_user_choices(),
            label="Введите имя пользователя или выберите из списка",
            interactive=True,
            value=None,  # По умолчанию пользователь не выбран
            allow_custom_value=False  # Исключает произвольные значения
        )

        # Логика обновления и действий
        def update_user_choices(show_inactive):
            """Обновляет список пользователей."""
            choices = prepare_user_choices(show_inactive)
            # Проверяем, что список не пустой
            if not choices:
                return {"choices": choices, "value": None}
            return {"choices": choices, "value": ""}

        refresh_button.click(
            fn=update_user_choices,
            inputs=[show_inactive_checkbox],
            outputs=user_dropdown
        )
        user_dropdown.change(
            fn=get_user_info,
            inputs=[user_dropdown],
            outputs=user_info_box
        )
        block_button.click(
            fn=dummy_action,
            inputs=[user_dropdown],
            outputs=user_info_box
        )
        delete_button.click(
            fn=dummy_action,
            inputs=[user_dropdown],
            outputs=user_info_box
        )
        archive_button.click(
            fn=dummy_action,
            inputs=[user_dropdown],
            outputs=user_info_box
        )
