#!/usr/bin/env python3
# gradio_admin/tabs/statistics_tab.py
# Вкладка "Statistics" для Gradio-интерфейса проекта wg_qr_generator

import gradio as gr
import pandas as pd
from gradio_admin.functions.table_helpers import update_table
from gradio_admin.functions.format_helpers import format_user_info
from gradio_admin.functions.user_records import load_user_records


def statistics_tab():
    """Возвращает вкладку статистики пользователей WireGuard."""
    with gr.Tab("🔍 Statistics"):
        with gr.Row():
            gr.Markdown("## Statistics")

        # Чекбокс Show inactive и кнопка Refresh
        with gr.Row():
            show_inactive = gr.Checkbox(label="Show inactive", value=True)
            refresh_button = gr.Button("Refresh")

        # Область для отображения информации о выбранном пользователе
        with gr.Row():
            selected_user_info = gr.Textbox(label="User Information", interactive=False)

        # Кнопки действий
        with gr.Row():
            block_button = gr.Button("Block")
            delete_button = gr.Button("Delete")

        # Поиск во всю ширину с кнопкой поиска
        with gr.Row():
            search_input = gr.Textbox(label="Search", placeholder="Enter data to filter...", interactive=True)
            search_button = gr.Button("Search")

        # Таблица с данными
        with gr.Row():
            stats_table = gr.Dataframe(
                headers=["👥 User's info", "🆔 Other info"],
                value=update_table(True),
                interactive=False,  # Таблица только для чтения
                wrap=True
            )

        # Функция для показа информации о пользователе
        def show_user_info(selected_data, query):
            """Показывает подробную информацию о выбранном пользователе."""
            print("[DEBUG] Вызов функции show_user_info")  # Отладка
            print(f"[DEBUG] Query: {query}")  # Отладка

            # Проверяем, был ли выполнен поиск
            if not query.strip():
                return "Please enter a query to filter user data and then click a cell to view user details and perform actions."

            # Проверяем, есть ли данные
            print(f"[DEBUG] Selected data: {selected_data}")  # Отладка
            if selected_data is None or (isinstance(selected_data, pd.DataFrame) and selected_data.empty):
                return "Select a row from the table!"
            try:
                # Если данные предоставлены в формате списка
                if isinstance(selected_data, list):
                    print(f"[DEBUG] Data format: list, data: {selected_data}")  # Отладка
                    row = selected_data
                # Если данные предоставлены в формате DataFrame
                elif isinstance(selected_data, pd.DataFrame):
                    print(f"[DEBUG] Data format: DataFrame, data:\n{selected_data}")  # Отладка
                    row = selected_data.iloc[0].values
                else:
                    return "Unsupported data format!"

                print(f"[DEBUG] Extracted row: {row}")  # Отладка

                # Загружаем информацию о пользователе
                username = row[0].replace("👤 User account : ", "") if len(row) > 0 else "N/A"
                records = load_user_records()
                user_data = records.get(username, {})

                # Форматируем данные для вывода
                user_info = format_user_info(username, user_data, row)
                print(f"[DEBUG] User info:\n{user_info}")  # Отладка
                return user_info.strip()
            except Exception as e:
                print(f"[DEBUG] Error: {e}")  # Отладка
                return f"Error processing data: {str(e)}"

        stats_table.select(
            fn=show_user_info,
            inputs=[stats_table, search_input],
            outputs=[selected_user_info]
        )

        # Обновление данных при нажатии кнопки "Refresh"
        def refresh_table(show_inactive):
            """Очищает строку поиска, сбрасывает информацию о пользователе и обновляет таблицу."""
            return "", "", update_table(show_inactive)

        refresh_button.click(
            fn=refresh_table,
            inputs=[show_inactive],
            outputs=[search_input, selected_user_info, stats_table]
        )

        # Поиск
        def search_and_update_table(query, show_inactive):
            """Фильтрует данные таблицы по запросу."""
            table = update_table(show_inactive)
            if query:
                table = [
                    row for row in table if query.lower() in " ".join(map(str, row)).lower()
                ]
            return table

        search_input.change(
            fn=search_and_update_table,
            inputs=[search_input, show_inactive],
            outputs=[stats_table]
        )

