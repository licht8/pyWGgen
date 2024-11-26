#!/usr/bin/env python3
# gradio_admin/main_interface.py

import gradio as gr

# Создаем объект интерфейса
with gr.Blocks(css="style.css") as admin_interface:
    with gr.Tab(label="🌱 Создать пользователя"):
        gr.Markdown("Интерфейс создания пользователя.")
    with gr.Tab(label="🔥 Удалить пользователя"):
        gr.Markdown("Интерфейс удаления пользователя.")
    with gr.Tab(label="🔍 Статистика"):
        gr.Markdown("Статистика WireGuard пользователей.")
