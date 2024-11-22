#!/usr/bin/env python3
# main_interface.py
## Главный интерфейс Gradio для управления проектом wg_qr_generator

import sys
import os
import gradio as gr

# Добавляем путь к корневой директории проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Импортируем функции для работы с пользователями
from gradio_admin.create_user import create_user
from gradio_admin.list_users import list_users
from gradio_admin.delete_user import delete_user
from gradio_admin.search_user import search_user
from gradio_admin.wg_users_stats import load_data  # Импорт статистики пользователей


# Функция для обновления таблицы
def update_table(show_inactive):
    table = load_data(show_inactive)
    formatted_table = []

    for row in table:
        user = row[0]
        allowed_ips = row[2]
        state = row[6]
        # Цветовая индикация статуса
        state_color = "green" if state == "active" else "red"

        formatted_table.append([
            f"{user}\n{allowed_ips}",  # User/IPs
            row[1],                   # Endpoints
            row[4],                   # Up (sent)
            row[3],                   # Down (received)
            row[5],                   # Recent handshake
            f"<span style='color: {state_color}'>{state}</span>"  # State
        ])
    return formatted_table


# Основной интерфейс
with gr.Blocks(css="style.css") as admin_interface:
    # Вкладка для создания пользователя
    with gr.Tab("Создание пользователя"):
        with gr.Row():
            gr.Markdown("## Создать нового пользователя")
        with gr.Column(scale=1, min_width=300):
            username_input = gr.Textbox(label="Имя пользователя", placeholder="Введите имя пользователя...")
            create_button = gr.Button("Создать пользователя")
            create_output = gr.Textbox(label="Результат создания", interactive=False)
            qr_code_image = gr.Image(label="QR-код", visible=False)

            def handle_create_user(username):
                """Обработчик для создания пользователя и отображения QR-кода."""
                result, qr_code_path = create_user(username)
                if qr_code_path:
                    return result, gr.update(visible=True, value=qr_code_path)
                return result, gr.update(visible=False)

            create_button.click(
                handle_create_user,
                inputs=username_input,
                outputs=[create_output, qr_code_image]
            )

    # Вкладка для списка пользователей
    with gr.Tab("Список пользователей"):
        with gr.Row():
            gr.Markdown("## Показать список пользователей")
        with gr.Column(scale=1, min_width=300):
            list_button = gr.Button("Показать пользователей")
            list_output = gr.Textbox(label="Список пользователей", interactive=False)
            list_button.click(list_users, outputs=list_output)

    # Вкладка для удаления пользователей
    with gr.Tab("Удаление пользователей"):
        with gr.Row():
            gr.Markdown("## Удалить пользователя")
        with gr.Column(scale=1, min_width=300):
            delete_input = gr.Textbox(label="Имя пользователя для удаления", placeholder="Введите имя пользователя...")
            delete_button = gr.Button("Удалить пользователя")
            delete_output = gr.Textbox(label="Результат удаления", interactive=False)
            delete_button.click(delete_user, inputs=delete_input, outputs=delete_output)

            # Добавляем кнопку для отображения списка пользователей
            list_button = gr.Button("Показать пользователей")
            list_output = gr.Textbox(label="Список пользователей", interactive=False)
            list_button.click(list_users, outputs=list_output)

    # Вкладка для поиска пользователей
    with gr.Tab("Поиск пользователей"):
        with gr.Row():
            gr.Markdown("## Поиск пользователей")
        with gr.Column(scale=1, min_width=300):
            search_input = gr.Textbox(label="Введите имя или IP", placeholder="Введите строку для поиска...")
            search_button = gr.Button("Поиск")
            search_output = gr.Textbox(label="Результат поиска", interactive=False)
            search_button.click(search_user, inputs=search_input, outputs=search_output)

    # Вкладка для статистики пользователей WireGuard
    with gr.Tab("Статистика пользователей"):
        with gr.Row():
            gr.Markdown("## Статистика пользователей WireGuard")
        with gr.Column(scale=1, min_width=300):
            show_inactive = gr.Checkbox(label="Показать неактивных пользователей", value=True)
            stats_table = gr.HTML(value="")  # Используем HTML для таблицы

            def render_table_html(show_inactive):
                """Генерация HTML-таблицы без полос прокрутки."""
                table_data = update_table(show_inactive)
                table_html = """
                <style>
                    table {
                        width: 100%;
                        border-collapse: collapse;
                    }
                    th, td {
                        text-align: left;
                        padding: 8px;
                    }
                    th {
                        background-color: #f2f2f2;
                    }
                </style>
                <table border="1">
                    <thead>
                        <tr>
                            <th>User/IPs</th>
                            <th>Endpoints</th>
                            <th>Up</th>
                            <th>Down</th>
                            <th>Recent</th>
                            <th>State</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                for row in table_data:
                    table_html += "<tr>" + "".join(f"<td>{col}</td>" for col in row) + "</tr>"
                table_html += "</tbody></table>"
                return table_html

            stats_table.value = render_table_html(True)

            # Обновляем таблицу при изменении состояния чекбокса
            show_inactive.change(fn=render_table_html, inputs=[show_inactive], outputs=[stats_table])

# Запуск интерфейса
if __name__ == "__main__":
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
