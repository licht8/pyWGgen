#!/usr/bin/env python3
# gradio_admin/tabs/create_user_tab.py
# Tab for creating users

import gradio as gr
from gradio_admin.functions.create_user import create_user

def create_user_tab():
    """
    Tab for creating WireGuard users.
    """
    gr.Markdown("# 🌱 Create User - Создание пользователя\n\nСоздай нового WireGuard пользователя с конфигом и QR кодом")
    
    username_input = gr.Textbox(label="Username", placeholder="Enter username...")
    email_input = gr.Textbox(label="Email (optional)", placeholder="Enter email...")
    telegram_input = gr.Textbox(label="Telegram ID (optional)", placeholder="Enter Telegram ID...")
    create_button = gr.Button("Create User")
    output_message = gr.Textbox(label="Result", interactive=False)
    qr_code_display = gr.Image(label="QR Code", visible=False)

    def handle_create_user(username, email, telegram_id):
        result, qr_code_path = create_user(username, email, telegram_id)
        
        # Разделяем успешные и ошибочные сообщения
        if result.startswith("✅"):
            return result, gr.update(visible=True, value=qr_code_path) if qr_code_path else gr.update(visible=False)
        else:
            return result, gr.update(visible=False)

    create_button.click(
        handle_create_user,
        inputs=[username_input, email_input, telegram_input],
        outputs=[output_message, qr_code_display]
    )
    
    return [username_input, email_input, telegram_input, create_button, output_message, qr_code_display]
