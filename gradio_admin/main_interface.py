#!/usr/bin/env python3
# gradio_admin/main_interface.py
# Основной интерфейс Gradio для управления проектом wg_qr_generator

import gradio as gr
from gradio_admin.tabs.create_user_tab import create_user_tab
from gradio_admin.tabs.delete_user_tab import delete_user_tab
from gradio_admin.tabs.statistics_tab import statistics_tab

# Создание интерфейса
with gr.Blocks() as admin_interface:
    with gr.Tab(label="🌱 Создать пользователя"):
        create_user_tab()
    
    with gr.Tab(label="🔥 Удалить пользователя"):
        delete_user_tab()
    
    with gr.Tab(label="🔍 Статистика"):
        statistics_tab()

if __name__ == "__main__":
    # Запуск интерфейса на 0.0.0.0 для внешнего доступа
    #admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True, )
    run_gradio_admin_interface()
