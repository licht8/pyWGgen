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
        print("[WARNING] Пользователь не выбран.")
        return "No user selected"

    user_id = selected_user.split("(")[-1].strip(")")
    user_records = load_user_records()
    for user in user_records.values():
        if user.get("user_id") == user_id:
            print(f"[DEBUG] Найден пользователь: {user.get('username')}")
            return json.dumps(user, indent=4)
    
    print("[WARNING] Пользователь не найден.")
    return "User not found."


def block_user(selected_user):
    """Блокирует пользователя."""
    print(f"[DEBUG] Блокировка пользователя: {selected_user}")
    if not selected_user:
        print("[WARNING] Невозможно заблокировать: пользователь не выбран.")
        return "No user selected"

    user_id = selected_user.split("(")[-1].strip(")")
    user_records = load_user_records()
    for username, user in user_records.items():
        if user.get("user_id") == user_id:
            user["status"] = "blocked"
            with open(USER_DB_PATH, "w") as f:
                json.dump(user_records, f, indent=4)
            print(f"[DEBUG] Пользователь {username} заблокирован.")
            return f"User {username} blocked."
    
    print("[WARNING] Пользователь для блокировки не найден.")
    return "User not found."


def delete_user(selected_user):
    """Удаляет пользователя."""
    print(f"[DEBUG] Удаление пользователя: {selected_user}")
    if not selected_user:
        print("[WARNING] Невозможно удалить: пользователь не выбран.")
        return "No user selected"

    user_id = selected_user.split("(")[-1].strip(")")
    user_records = load_user_records()
    for username, user in list(user_records.items()):
        if user.get("user_id") == user_id:
            del user_records[username]
            with open(USER_DB_PATH, "w") as f:
                json.dump(user_records, f, indent=4)
            print(f"[DEBUG] Пользователь {username} удален.")
            return f"User {username} deleted."
    
    print("[WARNING] Пользователь для удаления не найден.")
    return "User not found."


def statistics_tab():
    """Создает интерфейс вкладки статистики."""
    with gr.Tab("🔍 Statistics"):
        gr.Markdown("## Управление пользователями WireGuard")

        # Фильтры
        with gr.Row():
            show_inactive_checkbox = gr.Checkbox(label="Show inactive users", value=True)
            refresh_button = gr.Button("Refresh List")

        # Выбор пользователя
        user_dropdown = gr.Dropdown(choices=[], label="Выберите пользователя")

        # Подробная информация
        user_info_box = gr.Textbox(label="Информация о пользователе", lines=10, interactive=False)

        # Управление пользователями
        with gr.Row():
            block_button = gr.Button("Block User")
            delete_button = gr.Button("Delete User")

        # Связывание компонентов
        def update_user_choices(show_inactive):
            print("[DEBUG] Обновление списка пользователей...")
            choices = prepare_user_choices(show_inactive)
            return {"choices": choices}

        refresh_button.click(update_user_choices, inputs=[show_inactive_checkbox], outputs=user_dropdown)
        user_dropdown.change(get_user_info, inputs=[user_dropdown], outputs=user_info_box)
        block_button.click(block_user, inputs=[user_dropdown], outputs=user_info_box)
        delete_button.click(delete_user, inputs=[user_dropdown], outputs=user_info_box)
