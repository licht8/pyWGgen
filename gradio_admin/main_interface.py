#!/usr/bin/env python3
# main_interface.py
## Главный интерфейс Gradio для управления проектом wg_qr_generator

import sys
import os
import json
import gradio as gr
from datetime import datetime

# Добавляем путь к корневой директории проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Импортируем функции для работы с пользователями
from gradio_admin.create_user import create_user
from gradio_admin.delete_user import delete_user
from gradio_admin.wg_users_stats import load_data  # Импорт статистики пользователей


# Функция для форматирования времени
def format_time(iso_time):
    """Форматирует время из ISO 8601 в читаемый формат."""
    try:
        dt = datetime.fromisoformat(iso_time)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "N/A"


def calculate_time_remaining(expiry_time):
    """Вычисляет оставшееся время до истечения."""
    try:
        dt_expiry = datetime.fromisoformat(expiry_time)
        delta = dt_expiry - datetime.now()
        if delta.days >= 0:
            return f"{delta.days} days"
        return "Expired"
    except Exception:
        return "N/A"


# Функция для обновления таблицы
def update_table(show_inactive):
    """Форматирует данные таблицы."""
    table = load_data(show_inactive)
    formatted_rows = []

    for row in table:
        username = row[0]
        allowed_ips = row[2]
        recent = row[5]
        endpoint = row[1] or "N/A"
        up = row[4]
        down = row[3]
        status = row[6]
        created = row[7] if len(row) > 7 else "N/A"
        expires = row[8] if len(row) > 8 else "N/A"

        # Эмодзи для состояния
        recent_emoji = "🟢" if status == "active" else "🔴"

        # Формирование строк для пользователя
        formatted_rows.append([f"👤 {username}", f"⬆️ {up}"])
        formatted_rows.append([f"🌐 intIP {recent_emoji}  : {allowed_ips}", f"⬇️ {down}"])
        formatted_rows.append([f"🌎 extIP {recent_emoji}  : {endpoint}", f"📅 TimeLeft: {calculate_time_remaining(expires)}"])
        formatted_rows.append(["", ""])  # Пустая строка для разделения пользователей

    return formatted_rows


# Функция для загрузки информации о пользователе
def load_user_info(username):
    """Возвращает информацию о пользователе для отображения."""
    user_records_path = "/root/pyWGgen/wg_qr_generator/user/data/user_records.json"
    user_data = {}

    try:
        with open(user_records_path, "r") as f:
            user_data = json.load(f)
    except FileNotFoundError:
        print(f"[DEBUG] File not found: {user_records_path}")
    except Exception as e:
        print(f"[DEBUG] Error reading user records: {e}")

    user_info = user_data.get(username, {})
    created = format_time(user_info.get("created_at", "N/A"))
    expires = format_time(user_info.get("expires_at", "N/A"))
    address = user_info.get("address", "N/A")

    return f"""
👤 User: {username}
📧 Email: user@mail.wg
🌱 Created: {created}
🔥 Expires: {expires}
🌐 Internal IP: {address}
🌎 External IP: N/A
⬆️ Uploaded: N/A
⬇️ Downloaded: N/A
✅ Status: N/A
"""


# Функция для отображения информации о пользователе
def show_user_info(selected_data):
    """Показывает информацию о выбранном пользователе."""
    try:
        print("[DEBUG] Вызов функции show_user_info")
        print(f"[DEBUG] Selected data raw: {selected_data}")

        if selected_data is None or len(selected_data) == 0:
            return "First select data from the table!"

        if isinstance(selected_data, list) and len(selected_data) == 1:
            clicked_cell = selected_data[0]
            print(f"[DEBUG] Clicked cell: {clicked_cell}")

            # Определяем имя пользователя из клика
            for row in update_table(True):
                if clicked_cell in row:
                    username = row[0].replace("👤 ", "")  # Удаляем эмодзи
                    print(f"[DEBUG] Extracted username: {username}")

                    # Получение детальной информации о пользователе
                    user_info = load_user_info(username)
                    print(f"[DEBUG] User info:\n{user_info}")
                    return user_info.strip()

        return "Error: could not determine the user from the selected data."
    except Exception as e:
        print(f"[DEBUG] Error: {e}")
        return f"Error processing data: {str(e)}"


# Основной интерфейс
with gr.Blocks(css="style.css") as admin_interface:
    # Вкладка для создания пользователя
    with gr.Tab("Create"):
        with gr.Row():
            gr.Markdown("## Create a new user")
        with gr.Column(scale=1, min_width=300):
            username_input = gr.Textbox(label="Username", placeholder="Enter username...")
            create_button = gr.Button("Create User")
            create_output = gr.Textbox(label="Creation Result", interactive=False)
            qr_code_image = gr.Image(label="QR Code", visible=False)

            def handle_create_user(username):
                """Обработчик для создания пользователя и отображения QR-кода."""
                result, qr_code_path = create_user(username)
                if qr_code_path:
                    return result, gr.update(visible=True, value=qr_code_path)
                return result, gr.update(visible=False)

            create_button.click(
                handle_create_user,
                inputs=username_input,
                outputs=[create_output, qr_code_image]
            )

    # Вкладка для удаления пользователей
    with gr.Tab("Delete"):
        with gr.Row():
            gr.Markdown("## Delete a user")
        with gr.Column(scale=1, min_width=300):
            delete_input = gr.Textbox(label="Username to delete", placeholder="Enter username...")
            delete_button = gr.Button("Delete User")
            delete_output = gr.Textbox(label="Deletion Result", interactive=False)
            delete_button.click(delete_user, inputs=delete_input, outputs=delete_output)

    # Вкладка для статистики пользователей WireGuard
    with gr.Tab("Statistics"):
        with gr.Row():
            gr.Markdown("## User Statistics")
        with gr.Row():
            search_input = gr.Textbox(label="Search", placeholder="Enter data to filter...")
            refresh_button = gr.Button("Refresh")
            show_inactive = gr.Checkbox(label="Show inactive", value=True)
        with gr.Row():
            stats_table = gr.Dataframe(
                headers=["👥 User's info", "🆔 Other info"],
                value=update_table(True),
                interactive=False,
                wrap=True
            )
        with gr.Row():
            user_info_output = gr.Textbox(label="User Information", interactive=False)

        # Обработчики событий
        search_input.change(
            fn=lambda query, show_inactive: [
                update_table(show_inactive),
                "",
            ],
            inputs=[search_input, show_inactive],
            outputs=[stats_table, user_info_output],
        )

        refresh_button.click(
            fn=lambda show_inactive: update_table(show_inactive),
            inputs=[show_inactive],
            outputs=[stats_table],
        )

        stats_table.select(
            fn=show_user_info,
            inputs=[stats_table],
            outputs=[user_info_output],
        )

# Запуск интерфейса
if __name__ == "__main__":
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
