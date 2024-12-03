#!/usr/bin/env python3
# gradio_admin/main_interface.py

import gradio as gr
from gradio_admin.tabs.create_user_tab import create_user_tab
from gradio_admin.tabs.delete_user_tab import delete_user_tab
from gradio_admin.tabs.statistics_tab import statistics_tab
from gradio_admin.tabs.command_line_tab import create_command_line_tab

# Создание интерфейса
with gr.Blocks() as admin_interface:
    with gr.Tab(label="🌱 Создать пользователя"):
        create_user_tab()
    
    with gr.Tab(label="🔥 Удалить пользователя"):
        delete_user_tab()
    
    with gr.Tab(label="🔍 Статистика"):
        statistics_tab()
    
    with gr.Tab(label="💻 Эмуляция CLI"):
        create_command_line_tab()
