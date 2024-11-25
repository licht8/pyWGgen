#!/usr/bin/env python3
# main_interface.py
# Главный интерфейс Gradio для управления проектом wg_qr_generator

import sys
import os
import gradio as gr

# Добавляем путь к корню проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)  # Убедитесь, что путь добавлен первым

from modules.port_manager import handle_port_conflict  # Импорт управления портами

# Импортируем вкладки
from gradio_admin.tabs.delete_user_tab import delete_user_tab
from gradio_admin.tabs.statistics_tab import statistics_tab

ADMIN_PORT = 7860  # Порт для Gradio

def launch_gradio_interface():
    """
    Проверяет доступность порта, разрешает конфликты и запускает Gradio интерфейс.
    """
    conflict_action = handle_port_conflict(ADMIN_PORT)  # Проверка и обработка порта

    if conflict_action in {"ignore", "exit"}:
        return  # Возврат в меню или завершение программы

    if conflict_action == "kill":
        print(f"🔄 Порт {ADMIN_PORT} освобождён. Запуск Gradio...")

    # Основной интерфейс Gradio
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
                    from gradio_admin.create_user import create_user
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
        delete_user_tab()

        # Вкладка для статистики пользователей WireGuard
        statistics_tab()

    # Запуск интерфейса
    admin_interface.launch(server_name="0.0.0.0", server_port=ADMIN_PORT, share=True)

# Точка входа
if __name__ == "__main__":
    launch_gradio_interface()
