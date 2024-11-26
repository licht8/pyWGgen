#!/usr/bin/env python3
# main_interface.py
# Основной интерфейс Gradio для управления WireGuard пользователями

import gradio as gr
from gradio_admin.tabs.create_user_tab import create_user_tab
from gradio_admin.tabs.delete_user_tab import delete_user_tab
from gradio_admin.tabs.statistics_tab import statistics_tab

def main_interface():
    """
    Основной интерфейс для управления пользователями WireGuard с помощью вкладок Gradio.
    """
    with gr.Blocks() as interface:
        with gr.Tabs():
            with gr.Tab(label="🌱 Создать пользователя"):
                create_user_tab()

            with gr.Tab(label="🔥 Удалить пользователя"):
                delete_user_tab()

            with gr.Tab(label="🔍 Статистика"):
                statistics_tab()

    return interface

if __name__ == "__main__":
    # Запуск интерфейса
    app = main_interface()
    app.launch(server_name="0.0.0.0", server_port=7860)
