import gradio as gr
from gradio_admin.functions.table_helpers import update_table
from gradio_admin.functions.show_user_info import show_user_info
from gradio_admin.functions.user_records import load_user_records
from gradio_admin.create_user import create_user
from gradio_admin.delete_user import delete_user
from gradio_admin.functions.format_helpers import format_time, calculate_time_remaining


with gr.Blocks() as admin_interface:
    # Вкладка для создания пользователя
    with gr.Tab("🌱 Create"):
        with gr.Row():
            gr.Markdown("## Create a new user")
        with gr.Column(scale=1, min_width=300):
            username_input = gr.Textbox(label="Username", placeholder="Enter username...")
            create_button = gr.Button("Create User")
            create_output = gr.Textbox(label="Result", interactive=False)
            qr_code_image = gr.Image(label="QR Code", visible=False)

            def handle_create_user(username):
                """Обработчик для создания пользователя и отображения QR-кода."""
                result, qr_code_path = create_user(username)
                if qr_code_path:
                    return result, gr.update(visible=True, value=qr_code_path)
                return result, gr.update(visible=False)

            create_button.click(
                handle_create_user,
                inputs=username_input,
                outputs=[create_output, qr_code_image]
            )

    # Вкладка для удаления пользователей
    with gr.Tab("🔥 Delete"):
        with gr.Row():
            gr.Markdown("## Delete a user")
        with gr.Column(scale=1, min_width=300):
            delete_input = gr.Textbox(label="Username to delete", placeholder="Enter username...")
            delete_button = gr.Button("Delete User")
            delete_output = gr.Textbox(label="Result", interactive=False)
            delete_button.click(delete_user, inputs=delete_input, outputs=delete_output)

    # Вкладка для статистики пользователей WireGuard
    with gr.Tab("🔍 Statistics"):
        with gr.Row():
            gr.Markdown("## Statistics")
        with gr.Column(scale=1, min_width=300):
            search_input = gr.Textbox(label="Search", placeholder="Enter data to filter...")
            refresh_button = gr.Button("Refresh")
            show_inactive = gr.Checkbox(label="Show inactive", value=True)

        # Область для отображения информации о выбранном пользователе
        with gr.Row():
            selected_user_info = gr.Textbox(label="User Information", interactive=False)
        with gr.Row():
            block_button = gr.Button("Block")
            delete_button = gr.Button("Delete")

        # Таблица с данными
        with gr.Row():
            stats_table = gr.Dataframe(
                headers=["👥 User's info", "🆔 Other info"],
                value=update_table(True),
                interactive=True,
                wrap=True
            )

        def search_and_update_table(query, show_inactive):
            """Фильтрует данные таблицы по запросу."""
            table = update_table(show_inactive)
            if query:
                table = [
                    row for row in table if query.lower() in " ".join(map(str, row)).lower()
                ]
            return table

        def refresh_table(show_inactive):
            """Обновляет таблицу при нажатии Refresh."""
            return update_table(show_inactive)

        refresh_button.click(
            fn=refresh_table,
            inputs=[show_inactive],
            outputs=[stats_table]
        )

        search_input.change(
            fn=search_and_update_table,
            inputs=[search_input, show_inactive],
            outputs=[stats_table]
        )

        stats_table.select(
            fn=show_user_info,
            inputs=[stats_table, search_input],
            outputs=[selected_user_info]
        )

# Запуск интерфейса
if __name__ == "__main__":
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
