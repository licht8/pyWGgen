#!/usr/bin/env python3
# main_interface.py
## Главный интерфейс Gradio для управления проектом wg_qr_generator

import sys
import os

# Добавляем путь к корневой директории проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from gradio_admin.create_user import create_user
from gradio_admin.list_users import list_users
from gradio_admin.delete_user import delete_user
from gradio_admin.search_user import search_user

import gradio as gr

with gr.Blocks(css="style.css") as admin_interface:
    with gr.Tab("Создание пользователя"):
        with gr.Row():
            gr.Markdown("## Создать нового пользователя")

        with gr.Column(scale=1, min_width=300):
            username_input = gr.Textbox(label="Имя пользователя", placeholder="Введите имя пользователя...")
            create_button = gr.Button("Создать пользователя")
            create_output = gr.Textbox(label="Результат создания", interactive=False)
            qr_code_image = gr.Image(label="QR-код", visible=False)

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

if __name__ == "__main__":
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
