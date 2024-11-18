#!/usr/bin/env python3
# create_user.py
## Скрипт для создания пользователей через Gradio интерфейс

import gradio as gr
from gradio_admin.create_user import create_user

with gr.Blocks() as admin_interface:
    with gr.Tab("Создание пользователя"):
        # Заголовок вкладки
        with gr.Row(elem_id="centered-row"):
            gr.Markdown("## Создать нового пользователя")
        
        # Поля ввода и кнопка
        with gr.Column(scale=1, min_width=300):
            username_input = gr.Textbox(
                label="Имя пользователя",
                placeholder="Введите имя пользователя...",
                elem_id="username-input"
            )
            create_button = gr.Button("Создать пользователя", elem_id="create-button")
            create_output = gr.Textbox(
                label="Результат создания",
                interactive=False,
                elem_id="create-output"
            )
        
        # Связь кнопки и функции
        create_button.click(create_user, inputs=username_input, outputs=create_output)

if __name__ == "__main__":
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
