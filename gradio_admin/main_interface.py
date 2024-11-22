#!/usr/bin/env python3
"""
main_interface.py

Главный интерфейс Gradio для управления проектом wg_qr_generator.
"""

import gradio as gr
from functions.user_helpers import show_user_info
from functions.stats_helpers import load_user_records, calculate_time_remaining
from functions.format_helpers import format_time


def update_table(show_inactive):
    """
    Обновляет таблицу с данными пользователей.
    """
    records = load_user_records()
    rows = []

    for username, data in records.items():
        created = format_time(data.get("created_at", "N/A"))
        expires = format_time(data.get("expires_at", "N/A"))
        time_left = calculate_time_remaining(data.get("expires_at", "N/A"))

        rows.append([
            f"👤 User account : {username}",
            f"🌱 Created : {created}",
            f"🔥 Expires : {expires}",
            f"📅 Time Left : {time_left}"
        ])

    return rows


with gr.Blocks(css="style.css") as admin_interface:
    with gr.Tab("Statistics"):
        search_input = gr.Textbox(label="Search")
        stats_table = gr.Dataframe(headers=["👥 User's info"], value=update_table(True), interactive=True)
        user_info_output = gr.Textbox(label="User Information")

        search_input.change(fn=update_table, inputs=[search_input], outputs=[stats_table])
        stats_table.select(fn=show_user_info, inputs=[stats_table, search_input], outputs=[user_info_output])

if __name__ == "__main__":
    admin_interface.launch()
