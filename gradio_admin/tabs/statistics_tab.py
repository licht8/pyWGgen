# gradio_admin/tabs/statistics_tab.py
# Вкладка "Statistics" для Gradio-интерфейса проекта wg_qr_generator

import gradio as gr
import pandas as pd
from gradio_admin.functions.table_helpers import update_table
from gradio_admin.functions.format_helpers import format_user_info
from gradio_admin.functions.user_records import load_user_records

def statistics_tab():
    """Возвращает вкладку статистики пользователей WireGuard."""
    with gr.Row():
        gr.Markdown("## Statistics")

    # Чекбокс Show inactive и кнопка Refresh
    with gr.Row():
        show_inactive = gr.Checkbox(label="Show inactive", value=True)
        refresh_button = gr.Button("Refresh")

    # Область для отображения информации о выбранном пользователе
    with gr.Row():
        selected_user_info = gr.Textbox(
            label="User Information", 
            interactive=False, 
            value="Use the search below for filtering.",
            elem_id="user-info-block"  # Добавляем ID для CSS
        )

    # Кнопки действий на одной строке
    with gr.Row():
        block_button = gr.Button("Block", elem_id="block-button")
        delete_button = gr.Button("Delete", elem_id="delete-button")

    # Поле поиска
    with gr.Row():
        search_input = gr.Textbox(label="Search", placeholder="Enter data to filter...", interactive=True)

    # Надпись над таблицей
    with gr.Row():
        gr.Markdown("Click a cell to view user details after the search.", elem_id="table-help-text", elem_classes=["small-text"])

    # Таблица с данными
    with gr.Row():
        stats_table = gr.Dataframe(
            headers=["👤 User", "📊 Used", "📦 Limit", "⚡ St.", "💳 $", "UID", "🌐 IP Address"],  # Обновлено
            value=update_table(True),
            interactive=False,  # Таблица только для чтения
            wrap=True
        )

    # Функция для показа информации о пользователе
    def show_user_info(selected_data, query):
        """Показывает подробную информацию о выбранном пользователе."""
        # (Ваш код для обработки информации о пользователе)

    stats_table.select(
        fn=show_user_info,
        inputs=[stats_table, search_input],
        outputs=[selected_user_info]
    )

    # Обновление данных при нажатии кнопки "Refresh"
    def refresh_table(show_inactive):
        """Очищает строку поиска, сбрасывает информацию о пользователе и обновляет таблицу."""
        return "", "Please enter a query to filter user data and then Click a cell to view user details after the search. and perform actions.", update_table(show_inactive)

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
