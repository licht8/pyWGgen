# gradio_admin/tabs/delete_user_tab.py

import gradio as gr
from gradio_admin.functions.delete_user import delete_user  # Предполагаем, что эта функция уже реализована

def delete_user_tab():
    with gr.Row():
        gr.Markdown("## Удалить пользователя")
    with gr.Column(scale=1, min_width=300):
        username_input = gr.Textbox(label="Имя пользователя", placeholder="Введите имя пользователя...")
        delete_button = gr.Button("Удалить")
        delete_output = gr.Textbox(label="Результат", interactive=False)

        delete_button.click(
            delete_user,
            inputs=username_input,
            outputs=delete_output
        )
