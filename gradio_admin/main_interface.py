#!/usr/bin/env python3
# main_interface.py
# Главный интерфейс Gradio для управления WireGuard пользователями

import os
import sys
import gradio as gr

# Добавляем корневой путь в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from gradio_admin.tabs.create_user_tab import create_user_tab
from gradio_admin.tabs.delete_user_tab import delete_user_tab
from gradio_admin.tabs.statistics_tab import statistics_tab

def main():
    """
    Запуск Gradio интерфейса.
    """
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
