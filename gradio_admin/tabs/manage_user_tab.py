#!/usr/bin/env python3
# gradio_admin/tabs/manage_user_tab.py
# Tab for managing user deletion, blocking, and unblocking

import gradio as gr  # type: ignore
from gradio_admin.functions.delete_user import delete_user
from gradio_admin.functions.user_records import load_user_records
from gradio_admin.functions.block_user import block_user, unblock_user

def manage_user_tab():
    """Creates a tab for deleting, blocking, and unblocking WireGuard users."""
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

    with gr.Row():
        gr.Markdown("## Manage Users")

    with gr.Row():
        user_selector = gr.Dropdown(choices=get_user_list(), value="Select a user", interactive=True)
        refresh_button = gr.Button("Refresh List")

    with gr.Row():
        delete_button = gr.Button("Delete User")
        block_button = gr.Button("Block User")
        unblock_button = gr.Button("Unblock User")

    with gr.Row():
        result_display = gr.Textbox(label="Result", value="", lines=2, interactive=False)

    refresh_button.click(fn=refresh_user_list, inputs=[], outputs=[user_selector, result_display])
    delete_button.click(fn=handle_user_deletion, inputs=[user_selector], outputs=[user_selector, result_display])
    block_button.click(fn=handle_user_block, inputs=[user_selector], outputs=[user_selector, result_display])
    unblock_button.click(fn=handle_user_unblock, inputs=[user_selector], outputs=[user_selector, result_display])
