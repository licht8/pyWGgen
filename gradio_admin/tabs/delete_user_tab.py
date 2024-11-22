import gradio as gr
from gradio_admin.delete_user import delete_user

def delete_user_tab():
    """Создает вкладку для удаления пользователей."""
    with gr.Tab("🔥 Delete"):
        with gr.Row():
            gr.Markdown("## Delete a user")
        with gr.Column(scale=1, min_width=300):
            delete_input = gr.Textbox(label="Username to delete", placeholder="Enter username...")
            delete_button = gr.Button("Delete User")
            delete_output = gr.Textbox(label="Result", interactive=False)

            def handle_delete_user(username):
                """Обработчик для удаления пользователя."""
                return delete_user(username)

            delete_button.click(handle_delete_user, inputs=delete_input, outputs=delete_output)
