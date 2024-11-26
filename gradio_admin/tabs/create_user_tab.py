#!/usr/bin/env python3
# gradio_admin/tabs/create_user_tab.py
# Вкладка для создания пользователей

import gradio as gr
from gradio_admin.functions.create_user import create_user

def create_user_tab():
    """
    Вкладка для создания пользователей WireGuard.
    """
    username_input = gr.Textbox(label="Имя пользователя", placeholder="Введите имя пользователя...")
    email_input = gr.Textbox(label="Email (необязательно)", placeholder="Введите email...")
    telegram_input = gr.Textbox(label="Telegram ID (необязательно)", placeholder="Введите Telegram ID...")
    create_button = gr.Button("Создать пользователя")
    output_message = gr.Textbox(label="Результат", interactive=False)
    qr_code_display = gr.Image(label="QR-код", visible=False)

    def handle_create_user(username, email, telegram_id):
        result, qr_code_path = create_user(username, email, telegram_id)
        if qr_code_path:
            return result, gr.update(visible=True, value=qr_code_path)
        return result, gr.update(visible=False)

    create_button.click(
        handle_create_user,
        inputs=[username_input, email_input, telegram_input],
        outputs=[output_message, qr_code_display]
    )
    
    return [username_input, email_input, telegram_input, create_button, output_message, qr_code_display]
