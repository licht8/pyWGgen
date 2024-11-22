#!/usr/bin/env python3
# main_interface.py
## Главный интерфейс Gradio для управления проектом wg_qr_generator

import sys
import os
import gradio as gr
from datetime import datetime
import pandas as pd
import json

# Добавляем путь к корневой директории проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Пути к файлам
USER_RECORDS_PATH = os.path.join(project_root, "user/data/user_records.json")

# Импортируем функции для работы с пользователями
from gradio_admin.create_user import create_user
from gradio_admin.delete_user import delete_user
from gradio_admin.wg_users_stats import load_data


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


def load_user_records():
    """Загружает данные о пользователях из файла user_records.json."""
    try:
        with open(USER_RECORDS_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[DEBUG] user_records.json not found!")
        return {}
    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON decode error in user_records.json: {e}")
        return {}


# Функция для обновления таблицы
def update_table(show_inactive):
    """Форматирует данные таблицы с шестью строками на пользователя."""
    table = load_data(show_inactive)
    formatted_rows = []

    for row in table:
        username = row[0] if len(row) > 0 else "N/A"
        allowed_ips = row[2] if len(row) > 2 else "N/A"
        recent = row[5] if len(row) > 5 else "N/A"
        endpoint = row[1] if len(row) > 1 else "N/A"
        up = row[4] if len(row) > 4 else "N/A"
        down = row[3] if len(row) > 3 else "N/A"
        status = row[6] if len(row) > 6 else "N/A"
        created = row[7] if len(row) > 7 else "N/A"
        expires = row[8] if len(row) > 8 else "N/A"

        # Эмодзи для состояния
        recent_emoji = "🟢" if status == "active" else "🔴"
        state_emoji = "✅" if status == "active" else "❌"

        # Формирование строк для пользователя
        formatted_rows.append([f"👤 User account : {username}", f"📧 User e-mail : user@mail.wg"])
        formatted_rows.append([f"🌱 Created : {format_time(created)}", f"🔥 Expires : {format_time(expires)}"])
        formatted_rows.append([f"🌐 intIP {recent_emoji}  : {allowed_ips}", f"⬆️ up : {up}"])
        formatted_rows.append([f"🌎 extIP {recent_emoji}  : {endpoint}", f"⬇️ dw : {down}"])
        formatted_rows.append([f"📅 TimeLeft : {calculate_time_remaining(expires)}", f"State : {state_emoji}"])

        # Добавление пустой строки между пользователями
        formatted_rows.append(["", ""])

    return formatted_rows


# Основной интерфейс
with gr.Blocks(css="style.css") as admin_interface:
    # Вкладка для создания пользователя
    with gr.Tab("🌱 Create"):
        with gr.Row():
            gr.Markdown("## Create a new user")
        with gr.Column(scale=1, min_width=300):
            username_input = gr.Textbox(label="Username", placeholder="Enter username...")
            create_button = gr.Button("Create User")
            create_output = gr.Textbox(label="Result", interactive=False)
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
    with gr.Tab("🔥 Delete"):
        with gr.Row():
            gr.Markdown("## Delete a user")
        with gr.Column(scale=1, min_width=300):
            delete_input = gr.Textbox(label="Username to delete", placeholder="Enter username...")
            delete_button = gr.Button("Delete User")
            delete_output = gr.Textbox(label="Result", interactive=False)
            delete_button.click(delete_user, inputs=delete_input, outputs=delete_output)

    # Вкладка для статистики пользователей WireGuard
    with gr.Tab("🔍 Statistics"):
        with gr.Row():
            gr.Markdown("## Statistics")
        with gr.Column(scale=1, min_width=300):
            search_input = gr.Textbox(label="Search", placeholder="Enter data to filter...")
            refresh_button = gr.Button("Refresh")
            show_inactive = gr.Checkbox(label="Show inactive", value=True)

        # Область для отображения информации о выбранном пользователе
        with gr.Row():
            selected_user_info = gr.Textbox(label="User Information", interactive=False)
        with gr.Row():
            block_button = gr.Button("Block")
            delete_button = gr.Button("Delete")

        # Таблица с данными
        with gr.Row():
            stats_table = gr.Dataframe(
                headers=["👥 User's info", "🆔 Other info"],
                value=update_table(True),
                interactive=True,
                wrap=True
            )

        def show_user_info(selected_data, query):
            """Показывает подробную информацию о выбранном пользователе."""
            print("[DEBUG] Вызов функции show_user_info")  # Отладка
            print(f"[DEBUG] Query: {query}")  # Отладка

            # Проверяем, был ли выполнен поиск
            if not query.strip():
                return "Please enter a query to filter user data and then click a cell to view user details and perform actions."

            # Проверяем, есть ли данные
            print(f"[DEBUG] Selected data: {selected_data}")  # Отладка
            if selected_data is None or (isinstance(selected_data, pd.DataFrame) and selected_data.empty):
                return "Select a row from the table!"
            try:
                # Если данные предоставлены в формате списка
                if isinstance(selected_data, list):
                    print(f"[DEBUG] Data format: list, data: {selected_data}")  # Отладка
                    row = selected_data
                # Если данные предоставлены в формате DataFrame
                elif isinstance(selected_data, pd.DataFrame):
                    print(f"[DEBUG] Data format: DataFrame, data:\n{selected_data}")  # Отладка
                    row = selected_data.iloc[0].values
                else:
                    return "Unsupported data format!"

                print(f"[DEBUG] Extracted row: {row}")  # Отладка

                # Безопасно извлекаем данные, проверяя длину строки
                username = row[0].replace("👤 User account : ", "") if len(row) > 0 else "N/A"
                email = "user@mail.wg"  # Заглушка
                records = load_user_records()
                user_data = records.get(username, {})

                created = user_data.get("created_at", "N/A")
                expires = user_data.get("expires_at", "N/A")
                int_ip = user_data.get("address", "N/A")
                ext_ip = "N/A" if len(row) <= 4 else row[4].replace("🌎 extIP : ", "N/A")
                up = "N/A" if len(row) <= 5 else row[5].replace("⬆️ up : ", "N/A")
                down = "N/A" if len(row) <= 6 else row[6].replace("⬇️ dw : ", "N/A")
                state = "N/A" if len(row) <= 7 else row[7].replace("State : ", "N/A")

                # Формируем текстовый вывод
                user_info = f"""
👤 User: {username}
📧 Email: {email}
🌱 Created: {format_time(created)}
🔥 Expires: {format_time(expires)}
🌐 Internal IP: {int_ip}
🌎 External IP: {ext_ip}
⬆️ Uploaded: {up}
⬇️ Downloaded: {down}
✅ Status: {state}
"""
                print(f"[DEBUG] User info:\n{user_info}")  # Отладка
                return user_info.strip()
            except Exception as e:
                print(f"[DEBUG] Error: {e}")  # Отладка
                return f"Error processing data: {str(e)}"

        stats_table.select(
            fn=show_user_info,
            inputs=[stats_table, search_input],
            outputs=[selected_user_info]
        )

        # Обновление данных при нажатии кнопки "Refresh"
        refresh_button.click(
            fn=update_table,
            inputs=[show_inactive],
            outputs=[stats_table]
        )

        # Поиск
        def search_and_update_table(query, show_inactive):
            """Фильтрует данные таблицы по запросу."""
            table = update_table(show_inactive)
            if query:
                table = [
                    row for row in table if query.lower() in " ".join(map(str, row)).lower()
                ]
            return table

        search_input.change(
            fn=search_and_update_table,
            inputs=[search_input, show_inactive],
            outputs=[stats_table]
        )

# Запуск интерфейса
if __name__ == "__main__":
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
