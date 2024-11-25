#!/usr/bin/env python3
# main_interface.py
# Главный интерфейс Gradio для управления проектом wg_qr_generator

import sys
import os
import gradio as gr

# Добавляем путь к корню проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Импортируем вкладки
from gradio_admin.tabs.delete_user_tab import delete_user_tab
from gradio_admin.tabs.statistics_tab import statistics_tab
from gradio_admin.create_user import create_user

USER_RECORDS_JSON = "user/data/user_records.json"

def save_user_to_json(username, allowed_ips):
    """Сохраняет нового пользователя в user_records.json."""
    if not os.path.exists(USER_RECORDS_JSON):
        records = {}
    else:
        with open(USER_RECORDS_JSON, "r") as file:
            records = json.load(file)

    records[username] = {"allowed_ips": allowed_ips, "status": "active"}
    with open(USER_RECORDS_JSON, "w") as file:
        json.dump(records, file, indent=4)

    print(f"✅ Пользователь {username} добавлен в JSON.")

# Основной интерфейс
with gr.Blocks(css="style.css") as admin_interface:
    # Вкладка для создания пользователя
    with gr.Tab("🌱 Create"):
        with gr.Row():
            gr.Markdown("## Create a new user")
        with gr.Column(scale=1, min_width=300):
            username_input = gr.Textbox(label="Username", placeholder="Enter username...")
            allowed_ips_input = gr.Textbox(label="Allowed IPs", placeholder="Enter allowed IPs...")
            create_button = gr.Button("Create User")
            create_output = gr.Textbox(label="Result", interactive=False)
            qr_code_image = gr.Image(label="QR Code", visible=False)

            def handle_create_user(username, allowed_ips):
                """Обработчик для создания пользователя и отображения QR-кода."""
                result, qr_code_path = create_user(username)
                save_user_to_json(username, allowed_ips)
                if qr_code_path:
                    return result, gr.update(visible=True, value=qr_code_path)
                return result, gr.update(visible=False)

            create_button.click(
                handle_create_user,
                inputs=[username_input, allowed_ips_input],
                outputs=[create_output, qr_code_image]
            )

    # Вкладка для удаления пользователей
    delete_user_tab()

    # Вкладка для статистики пользователей WireGuard
    statistics_tab()

# Запуск интерфейса
if __name__ == "__main__":
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
