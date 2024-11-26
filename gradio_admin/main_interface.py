#!/usr/bin/env python3
# main_interface.py

import gradio as gr

# Импорт вкладок
from gradio_admin.tabs.create_user_tab import create_user_tab
from gradio_admin.tabs.delete_user_tab import delete_user_tab
from gradio_admin.tabs.statistics_tab import statistics_tab

def main():
    """Основной интерфейс Gradio."""
    with gr.Blocks() as app:
        gr.Markdown("## 🌐 WireGuard User Management Interface")
        with gr.Tab(label="🌱 Создать пользователя"):
            create_user_tab()
        with gr.Tab(label="🔥 Удалить пользователя"):
            delete_user_tab()
        with gr.Tab(label="🔍 Статистика"):
            statistics_tab()
    app.launch(server_port=7860, share=False)

if __name__ == "__main__":
    main()
