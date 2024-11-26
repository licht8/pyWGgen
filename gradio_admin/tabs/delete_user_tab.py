#!/usr/bin/env python3
# gradio_admin/tabs/delete_user_tab.py
# Вкладка для удаления пользователей

import gradio as gr
from gradio_admin.functions.delete_user import delete_user

def delete_user_tab():
    """
    Вкладка для удаления пользователей WireGuard.
    """
    username_input = gr.Textbox(label="Имя пользователя", placeholder="Введите имя пользователя...")
    delete_button = gr.Button("Удалить пользователя")
    output_message = gr.Textbox(label="Результат", interactive=False)

    def handle_delete_user(username):
        return delete_user(username)

    delete_button.click(
        handle_delete_user,
        inputs=username_input,
        outputs=output_message
    )
    
    return [username_input, delete_button, output_message]
