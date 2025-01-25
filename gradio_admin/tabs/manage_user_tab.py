#!/usr/bin/env python3
import gradio as gr
from gradio_admin.functions.delete_user import delete_user
from gradio_admin.functions.user_records import load_user_records
from gradio_admin.functions.block_user import block_user, unblock_user
from sync import sync_users_from_config_paths

def manage_user_tab():
    def get_user_list():
        records = load_user_records()
        user_list = []
        for username, user_data in records.items():
            status = user_data.get("status", "unknown")
            display_status = f"({status.capitalize()})" if status else ""
            user_list.append(f"{username} {display_status}".strip())
        return ["Select a user"] + user_list

    def refresh_user_list():
        return gr.update(choices=get_user_list(), value="Select a user"), "User list updated."

    def handle_user_deletion(selected_user):
        username = selected_user.split(" ")[0]
        success = delete_user(username)
        if success:
            return gr.update(choices=get_user_list(), value="Select a user"), f"User '{username}' deleted successfully."
        return gr.update(), f"Failed to delete user '{username}'."

    def handle_user_block(selected_user):
        username = selected_user.split(" ")[0]
        success, message = block_user(username)
        return gr.update(choices=get_user_list(), value="Select a user"), message

    def handle_user_unblock(selected_user):
        username = selected_user.split(" ")[0]
        success, message = unblock_user(username)
        return gr.update(choices=get_user_list(), value="Select a user"), message

    def handle_sync(config_dir_str, qr_dir_str):
        success, log = sync_users_from_config_paths(config_dir_str, qr_dir_str)
        return log

    # Вместо gr.Box() используем gr.Group()
    with gr.Group():
        gr.Markdown("<h2 style='text-align:center; color:#4CAF50;'>Manage WireGuard Users</h2>")

        with gr.Row():
            user_selector = gr.Dropdown(
                choices=get_user_list(), 
                value="Select a user", 
                label="User List",
                interactive=True
            )
            refresh_button = gr.Button("Refresh List")

        with gr.Row():
            delete_button = gr.Button("Delete User")
            block_button = gr.Button("Block User")
            unblock_button = gr.Button("Unblock User")

        result_display = gr.Textbox(label="Result", value="", lines=3, interactive=False)

        # Если Accordion тоже отсутствует в вашей версии Gradio, уберите with gr.Accordion(...) 
        with gr.Accordion("Synchronization Settings", open=False):
            config_dir_input = gr.Textbox(
                label="Config Directory Path",
                value="",
                lines=1,
                placeholder="/path/to/configs"
            )
            qr_dir_input = gr.Textbox(
                label="QR Code Directory Path",
                value="",
                lines=1,
                placeholder="/path/to/qrcodes"
            )
            sync_button = gr.Button("Synchronize")

        # Привязка функций к кнопкам
        refresh_button.click(
            fn=refresh_user_list,
            inputs=[],
            outputs=[user_selector, result_display]
        )
        delete_button.click(
            fn=handle_user_deletion,
            inputs=[user_selector],
            outputs=[user_selector, result_display]
        )
        block_button.click(
            fn=handle_user_block,
            inputs=[user_selector],
            outputs=[user_selector, result_display]
        )
        unblock_button.click(
            fn=handle_user_unblock,
            inputs=[user_selector],
            outputs=[user_selector, result_display]
        )
        sync_button.click(
            fn=handle_sync,
            inputs=[config_dir_input, qr_dir_input],
            outputs=[result_display]
        )
