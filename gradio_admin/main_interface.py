# gradio_admin/main_interface.py

import gradio as gr
from gradio_admin.tabs.create_user_tab import create_user_tab
from gradio_admin.tabs.delete_user_tab import delete_user_tab
from gradio_admin.tabs.statistics_tab import statistics_tab

with gr.Blocks(css="style.css") as admin_interface:
    with gr.Tab(label="🌱 Создать пользователя"):
        create_user_tab()

    with gr.Tab(label="🔥 Удалить пользователя"):
        delete_user_tab()

    with gr.Tab(label="🔍 Статистика"):
        statistics_tab()

if __name__ == "__main__":
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
