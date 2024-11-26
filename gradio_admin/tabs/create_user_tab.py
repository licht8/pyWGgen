# gradio_admin/tabs/create_user_tab.py
# Вкладка Gradio для создания пользователя

import gradio as gr
from gradio_admin.functions.create_user import create_user

def create_user_tab():
    """
    Функция для создания вкладки Gradio для добавления нового пользователя.
    """
    with gr.Blocks() as tab:
        gr.Markdown("## Создание нового пользователя")
        
        username = gr.Textbox(label="Имя пользователя", placeholder="Введите имя пользователя", required=True)
        email = gr.Textbox(label="Электронная почта (необязательно)", placeholder="Введите email")
        telegram_id = gr.Textbox(label="Telegram ID (необязательно)", placeholder="Введите Telegram ID")

        output = gr.Textbox(label="Результат", interactive=False)

        def handle_create_user(username, email, telegram_id):
            # Вызываем функцию из create_user.py
            status, qr_path = create_user(username, email, telegram_id)
            return f"{status}\nQR-код: {qr_path}" if qr_path else status

        create_button = gr.Button("Создать пользователя")
        create_button.click(
            fn=handle_create_user,
            inputs=[username, email, telegram_id],
            outputs=[output]
        )

    return tab
