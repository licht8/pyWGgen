#!/usr/bin/env python3
# create_user_tab.py
# Вкладка для создания пользователей WireGuard

import gradio as gr
from gradio_admin.functions.create_user import create_user

def create_user_tab():
    """Вкладка для создания пользователей."""
    with gr.Row():
        gr.Markdown("### 🌱 Создать нового пользователя")

    username = gr.Textbox(label="Имя пользователя", placeholder="Введите имя")
    email = gr.Textbox(label="Email (опционально)")
    telegram_id = gr.Textbox(label="Telegram ID (опционально)")
    result = gr.Textbox(label="Результат", interactive=False)

    def handle_create(username, email, telegram_id):
        return create_user(username, email, telegram_id)[0]

    gr.Button("Создать").click(handle_create, inputs=[username, email, telegram_id], outputs=[result])
