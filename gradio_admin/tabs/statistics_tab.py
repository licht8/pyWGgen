#!/usr/bin/env python3
# gradio_admin/tabs/statistics_tab.py
# Вкладка "Statistics" для Gradio-интерфейса проекта wg_qr_generator

import gradio as gr
import pandas as pd
from gradio_admin.functions.table_helpers import update_table, search_and_update_table
from gradio_admin.functions.show_user_info import show_user_info


def statistics_tab():
    """Создает вкладку 'Statistics' для интерфейса Gradio."""
    with gr.Tab("🔍 Statistics"):
        with gr.Row():
            gr.Markdown("## Statistics")

        # Чекбокс Show inactive
        with gr.Row():
            show_inactive = gr.Checkbox(label="Show inactive", value=True)

        # Кнопка Refresh
        with gr.Row():
            refresh_button = gr.Button("Refresh")

        # Поле для отображения информации о выбранном пользователе
        with gr.Row():
            selected_user_info = gr.Textbox(label="User Information", interactive=False)

        # Поиск
        with gr.Row():
            search_input = gr.Textbox(label="Search", placeholder="Enter data to filter...", scale=8)
            search_button = gr.Button("Search", scale=1)

        # Кнопки действий
        with gr.Row():
            block_button = gr.Button("Block")
            delete_button = gr.Button("Delete")

        # Таблица с данными
        with gr.Row():
            stats_table = gr.Dataframe(
                headers=["👥 User's info", "🆔 Other info"],
                value=update_table(True),
                interactive=True,
                wrap=True
            )

        # Связь кнопки Refresh с обновлением таблицы и очисткой поля поиска и информации
        def refresh_table(show_inactive):
            """Очищает строку поиска, сбрасывает информацию о пользователе и обновляет таблицу."""
            return "", "", update_table(show_inactive)

        refresh_button.click(
            fn=refresh_table,
            inputs=[show_inactive],
            outputs=[search_input, selected_user_info, stats_table]
        )

        # Связь кнопки Search с перекидыванием к таблице
        def search_jump_to_table(query):
            """Фильтрует таблицу и возвращает результаты."""
            return search_and_update_table(query, show_inactive.value)

        search_button.click(
            fn=search_jump_to_table,
            inputs=[search_input],
            outputs=[stats_table]
        )

        # Связь поисковой строки с таблицей
        search_input.change(
            fn=search_and_update_table,
            inputs=[search_input, show_inactive],
            outputs=[stats_table]
        )

        # Связь клика по таблице с отображением информации о пользователе
        stats_table.select(
            fn=show_user_info,
            inputs=[stats_table, search_input],
            outputs=[selected_user_info]
        )
