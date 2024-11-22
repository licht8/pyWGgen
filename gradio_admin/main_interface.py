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
    """Форматирует данные таблицы в соответствии с новой структурой."""
    table = load_data(show_inactive)
    formatted_table = []

    for row in table:
        user = row[0]
        allowed_ips = row[2]
        recent = row[5]
        endpoints = row[1] or "N/A"
        up = row[4]
        down = row[3]
        state = row[6]

        # Эмодзи для Recent
        recent_emoji = "🟢" if state == "active" else "🔴"

        # Эмодзи для State
        state_emoji = "✅" if state == "active" else "❌"

        # Форматирование строк в первом и втором столбце
        first_col = f"{user}\n{allowed_ips} {recent_emoji}\n{endpoints}"
        second_col = f"Up: {up}\nDown: {down}\nState: {state_emoji}"

        formatted_table.append([first_col, second_col])

    return formatted_table


# Основной интерфейс
with gr.Blocks(css="style.css") as admin_interface:
    # Изменение заголовка страницы
    with gr.Row():
        gr.Markdown("## Статистика")

    # Поля поиска и управления
    with gr.Row():
        search_input = gr.Textbox(label="Поиск", placeholder="Введите данные для фильтрации...")
        refresh_button = gr.Button("Обновить")
        show_inactive = gr.Checkbox(label="Показать неактивных", value=True)

    # Таблица статистики
    with gr.Row():
        stats_table = gr.Dataframe(
            headers=["User/IPs", "Up/Down"],
            value=update_table(True),
            interactive=False,
            wrap=True
        )

        def search_and_update_table(query, show_inactive):
            """Фильтрует данные таблицы по запросу."""
            table = update_table(show_inactive)
            if query:
                table = [row for row in table if query.lower() in " ".join(map(str, row)).lower()]
            return table

        search_input.change(
            fn=search_and_update_table,
            inputs=[search_input, show_inactive],
            outputs=[stats_table]
        )

        refresh_button.click(
            fn=update_table,
            inputs=[show_inactive],
            outputs=[stats_table]
        )

# Запуск интерфейса
if __name__ == "__main__":
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
