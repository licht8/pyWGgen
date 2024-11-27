#!/usr/bin/env python3
# statistics_tab.py
# Вкладка "Statistics" Gradio-интерфейса wg_qr_generator

import gradio as gr
import json
import os
from settings import USER_DB_PATH  # Путь к JSON с данными пользователей


def load_user_records():
    """Загружает данные пользователей из JSON."""
    print("[DEBUG] Загрузка данных пользователей из JSON...")
    if not os.path.exists(USER_DB_PATH):
        print("[ERROR] Файл JSON с пользователями не найден!")
        return {}

    with open(USER_DB_PATH, "r") as f:
        data = json.load(f)
    print(f"[DEBUG] Загружено {len(data)} пользователей.")
    return data


def prepare_user_choices(show_inactive=True):
    """Создает список пользователей для Dropdown."""
    print(f"[DEBUG] Подготовка списка пользователей. Show inactive: {show_inactive}")
    user_records = load_user_records()
    user_choices = []

    for user in user_records.values():
        if not show_inactive and user.get("status") != "active":
            continue
        user_choices.append(f"{user['username']} ({user['user_id']})")
    
    print(f"[DEBUG] Подготовлено {len(user_choices)} записей для выбора.")
    return user_choices


def get_user_info(selected_user):
    """Возвращает подробную информацию о пользователе."""
    print(f"[DEBUG] Запрос информации о выбранном пользователе: {selected_user}")
    if not selected_user:
        print("[INFO] Пользователь не выбран.")
        return "Введите имя пользователя в поле выше или выберите из выпадающего списка. После выбора появится информация о пользователе."

    user_id = selected_user.split("(")[-1].strip(")")
    user_records = load_user_records()
    for user in user_records.values():
        if user.get("user_id") == user_id:
            print(f"[DEBUG] Найден пользователь: {user.get('username')}")
            return json.dumps(user, indent=4)
    
    print("[WARNING] Пользователь не найден.")
    return "Пользователь не найден. Проверьте ввод."


def dummy_action(selected_user):
    """Заглушка для кнопок."""
    if not selected_user:
        return "Пожалуйста, выберите пользователя для выполнения действий."
    return f"Действие для пользователя: {selected_user}"


def statistics_tab():
    """Создает интерфейс вкладки статистики."""
    with gr.Tab("🔍 Statistics"):
        gr.Markdown("## Управление пользователями WireGuard")

        # Фильтры и кнопка обновления
        with gr.Row():
            show_inactive_checkbox = gr.Checkbox(label="Show inactive users", value=True)
            refresh_button = gr.Button("Refresh List")

        # Выбор пользователя
        user_dropdown = gr.Dropdown(
            choices=prepare_user_choices(),
            label="Введите имя пользователя или выберите из списка",
            interactive=True
        )

        # Подробная информация
        user_info_box = gr.Textbox(
            label="Информация о пользователе",
            lines=10,
            interactive=False,
            value="Введите имя пользователя в поле выше или выберите из выпадающего списка. После выбора появится информация о пользователе."
        )

        # Управление пользователями
        with gr.Row():
            block_button = gr.Button("Block User")
            delete_button = gr.Button("Delete User")
            archive_button = gr.Button("Archive User")

        # Связывание компонентов
        def update_user_choices(show_inactive):
            print("[DEBUG] Обновление списка пользователей...")
            choices = prepare_user_choices(show_inactive)
            return {"choices": choices, "value": None}

        refresh_button.click(fn=update_user_choices, inputs=[show_inactive_checkbox], outputs=user_dropdown)
        user_dropdown.change(fn=get_user_info, inputs=[user_dropdown], outputs=user_info_box)
        block_button.click(fn=dummy_action, inputs=[user_dropdown], outputs=user_info_box)
        delete_button.click(fn=dummy_action, inputs=[user_dropdown], outputs=user_info_box)
        archive_button.click(fn=dummy_action, inputs=[user_dropdown], outputs=user_info_box)
