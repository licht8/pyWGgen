#!/usr/bin/env python3
# main_interface.py
## Главный интерфейс Gradio для управления проектом wg_qr_generator

import sys
import os

# Добавляем путь к корневой директории проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from gradio_admin.create_user import create_user
from gradio_admin.list_users import list_users
from gradio_admin.delete_user import delete_user
from gradio_admin.search_user import search_user

import gradio as gr

with gr.Blocks() as admin_interface:
    with gr.Tab("Создание пользователя"):
        # Заголовок вкладки
        with gr.Row():
            gr.Markdown("## Создать нового пользователя")
        # Поля для создания
        with gr.Column(scale=1, min_width=300):
            username_input = gr.Textbox(label="Имя пользователя", placeholder="Введите имя пользователя...")
            create_button = gr.Button("Создать пользователя")
            create_output = gr.Textbox(label="Результат создания", interactive=False)
            create_button.click(create_user, inputs=username_input, outputs=create_output)

    with gr.Tab("Список пользователей"):
        # Список пользователей
        with gr.Row():
            gr.Markdown("## Показать список пользователей")
        with gr.Column(scale=1, min_width=300):
            list_button = gr.Button("Показать пользователей")
            list_output = gr.Textbox(label="Список пользователей", interactive=False)
            list_button.click(list_users, outputs=list_output)

    with gr.Tab("Удаление пользователей"):
        # Удаление пользователей
        with gr.Row():
            gr.Markdown("## Удалить пользователя")
        with gr.Column(scale=1, min_width=300):
            delete_input = gr.Textbox(label="Имя пользователя для удаления", placeholder="Введите имя пользователя...")
            delete_button = gr.Button("Удалить пользователя")
            delete_output = gr.Textbox(label="Результат удаления", interactive=False)
            delete_button.click(delete_user, inputs=delete_input, outputs=delete_output)

    with gr.Tab("Поиск пользователей"):
        # Поиск пользователей
        with gr.Row():
            gr.Markdown("## Поиск пользователей")
        with gr.Column(scale=1, min_width=300):
            search_input = gr.Textbox(label="Введите имя или IP", placeholder="Введите строку для поиска...")
            search_button = gr.Button("Поиск")
            search_output = gr.Textbox(label="Результат поиска", interactive=False)
            search_button.click(search_user, inputs=search_input, outputs=search_output)

if __name__ == "__main__":
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
