#!/usr/bin/env python3
# create_user_tab.py
# Вкладка для создания пользователей WireGuard

import sys
import os

# Устанавливаем путь к корню проекта для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from gradio_admin.functions.create_user import create_user  # Импорт функции

import gradio as gr

def create_user_tab():
    """
    Вкладка для создания пользователей WireGuard.
    """
    with gr.Row():
        gr.Markdown("### 🌱 Создать нового пользователя")

    with gr.Row():
        username = gr.Textbox(label="Имя пользователя", placeholder="Введите имя пользователя")
        email = gr.Textbox(label="Email (необязательно)", placeholder="Введите email")
        telegram_id = gr.Textbox(label="Telegram ID (необязательно)", placeholder="Введите Telegram ID")

    result = gr.Textbox(label="Результат операции", interactive=False)

    def handle_create_user(username, email, telegram_id):
        """
        Обработчик для создания пользователя.
        """
        message, qr_path = create_user(username, email, telegram_id)
        return message

    create_button = gr.Button("Создать пользователя")
    create_button.click(handle_create_user, inputs=[username, email, telegram_id], outputs=[result])
