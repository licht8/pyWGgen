#!/usr/bin/env python3
# gradio_admin/main_interface.py
# Основной интерфейс Gradio для проекта

import gradio as gr
from gradio_admin.tabs.create_user_tab import create_user_tab
from gradio_admin.tabs.delete_user_tab import delete_user_tab
from gradio_admin.tabs.statistics_tab import statistics_tab

# Создание интерфейса
with gr.Blocks() as admin_interface:
    # Добавляем вкладки
    create_user_tab()
    delete_user_tab()
    statistics_tab()

if __name__ == "__main__":
    # Запуск Gradio интерфейса
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
