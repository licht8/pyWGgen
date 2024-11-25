#!/usr/bin/env python3
# main_interface.py
# Главный интерфейс Gradio для управления проектом wg_qr_generator

import sys
import os
import gradio as gr

# Добавляем путь к корню проекта
current_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

# Импортируем необходимые модули
from modules.port_manager import handle_port_conflict  # Управление портами
from modules.utils import get_wireguard_subnet

# Основной интерфейс
with gr.Blocks(css="style.css") as admin_interface:
    # Вкладка для управления пользователями
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
                try:
                    from gradio_admin.create_user import create_user
                    result, qr_code_path = create_user(username)
                    if qr_code_path:
                        return result, gr.update(visible=True, value=qr_code_path)
                    return result, gr.update(visible=False)
                except Exception as e:
                    return f"❌ Ошибка: {e}", gr.update(visible=False)

            create_button.click(
                handle_create_user,
                inputs=username_input,
                outputs=[create_output, qr_code_image]
            )

    # Вкладка для статистики
    with gr.Tab("📊 Statistics"):
        with gr.Row():
            gr.Markdown("## WireGuard Statistics")
        # Здесь можно добавить функционал для отображения статистики

# Проверка и обработка конфликтов порта
if __name__ == "__main__":
    port = 7860  # Порт Gradio
    port_status = handle_port_conflict(port)
    if port_status == "ok":
        admin_interface.launch(server_name="0.0.0.0", server_port=port, share=True)
    else:
        print("⚠️ Запуск Gradio отменён.")
