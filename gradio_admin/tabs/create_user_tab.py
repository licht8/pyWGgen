# gradio_admin/tabs/create_user_tab.py

import gradio as gr
from gradio_admin.functions.create_user import create_user  # Предполагаем, что эта функция уже реализована

def create_user_tab():
    with gr.Row():
        gr.Markdown("## Создать нового пользователя")
    with gr.Column(scale=1, min_width=300):
        username_input = gr.Textbox(label="Имя пользователя", placeholder="Введите имя пользователя...")
        create_button = gr.Button("Создать")
        create_output = gr.Textbox(label="Результат", interactive=False)
        qr_code_image = gr.Image(label="QR-код", visible=False)

        def handle_create_user(username):
            result, qr_code_path = create_user(username)
            if qr_code_path:
                return result, gr.update(visible=True, value=qr_code_path)
            return result, gr.update(visible=False)

        create_button.click(
            handle_create_user,
            inputs=username_input,
            outputs=[create_output, qr_code_image]
        )
