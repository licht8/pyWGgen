#!/usr/bin/env python3
# main_interface.py
# Главный интерфейс Gradio для управления проектом wg_qr_generator

import sys
import os
import gradio as gr

# Настройка путей
current_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

# Импорт необходимых модулей
from modules.port_manager import handle_port_conflict  # Управление портами
from gradio_admin.tabs.create_user_tab import create_user_tab
from gradio_admin.tabs.delete_user_tab import delete_user_tab
from gradio_admin.tabs.statistics_tab import statistics_tab

# Создание интерфейса Gradio
with gr.Blocks(css="style.css") as admin_interface:
    # Вкладка "Создать пользователя"
    with gr.Tab("👤 Создать"):
        create_user_tab()

    # Вкладка "Удалить пользователя"
    with gr.Tab("🔥 Удалить"):
        delete_user_tab()

    # Вкладка "Статистика"
    with gr.Tab("🔍 Статистика"):
        statistics_tab()

# Проверка и обработка конфликтов порта перед запуском
if __name__ == "__main__":
    port = 7860  # Порт для интерфейса
    port_status = handle_port_conflict(port)
    if port_status == "ok":
        admin_interface.launch(server_name="0.0.0.0", server_port=port, share=True)
    else:
        print("⚠️ Запуск Gradio отменён из-за конфликта порта.")
