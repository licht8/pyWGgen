#!/usr/bin/env python3
# gradio_admin/tabs/delete_user_tab.py
# Вкладка для удаления пользователей

import gradio as gr # type: ignore
from gradio_admin.functions.delete_user import delete_user
from gradio_admin.functions.user_records import load_user_records
from gradio_admin.functions.show_user_info import show_user_info

def delete_user_tab():
    """Создает вкладку для удаления пользователей WireGuard."""
    # Загрузка пользователей из базы
    def get_user_list():
        records = load_user_records()
        return ["Select a user"] + list(records.keys())

    # Поле для выбора пользователя
    with gr.Row():
        gr.Markdown("## Delete Users")

    with gr.Row():
        # Выпадающий список для выбора пользователя
        user_selector = gr.Dropdown(
            label="Select User",
            choices=get_user_list(),
            value="Select a user",
            interactive=True
        )
        # Кнопка для обновления списка
        refresh_list_button = gr.Button("Refresh List")

    # Информация о выбранном пользователе
    with gr.Row():
        user_info_display = gr.Textbox(label="User Info", value="", lines=5, interactive=False)

    # Кнопка для удаления
    with gr.Row():
        delete_button = gr.Button("Delete User")

    # Результат удаления
    with gr.Row():
        result_display = gr.Textbox(label="Result", value="", lines=2, interactive=False)

    # Функция для обновления списка пользователей
    def refresh_user_list():
        return gr.update(choices=get_user_list(), value="Select a user"), "User list updated."

    refresh_list_button.click(
        fn=refresh_user_list,
        inputs=[],
        outputs=[user_selector, result_display]
    )

    # Обновление информации о выбранном пользователе
    def display_user_info(selected_user):
        if not selected_user or selected_user == "Select a user":
            return "No user selected."
        user_info = show_user_info(selected_user)
        return user_info

    user_selector.change(
        fn=display_user_info,
        inputs=[user_selector],
        outputs=[user_info_display]
    )

    # Удаление пользователя
    def handle_user_deletion(selected_user):
        if not selected_user or selected_user == "Select a user":
            return "No user selected to delete."
        success = delete_user(selected_user)
        if success:
            return gr.update(choices=get_user_list(), value="Select a user"), f"User '{selected_user}' deleted successfully."
        else:
            return gr.update(), f"Failed to delete user '{selected_user}'."

    delete_button.click(
        fn=handle_user_deletion,
        inputs=[user_selector],
        outputs=[user_selector, result_display]
    )