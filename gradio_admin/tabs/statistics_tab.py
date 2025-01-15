# gradio_admin/tabs/statistics_tab.py
# Вкладка "Statistics" для Gradio-интерфейса проекта wg_qr_generator

import gradio as gr # type: ignore
import pandas as pd # type: ignore
from gradio_admin.functions.user_records import load_user_records
from gradio_admin.functions.format_helpers import format_time
from gradio_admin.functions.table_helpers import update_table
from gradio_admin.functions.format_helpers import format_user_info
from gradio_admin.functions.user_records import load_user_records
from gradio_admin.functions.show_user_info import show_user_info
from modules.traffic_updater import update_traffic_data
from settings import USER_DB_PATH

def statistics_tab():
    """Создает вкладку статистики пользователей WireGuard."""
    with gr.Row():
        gr.Markdown("## Statistics")

    # Чекбокс Show inactive и кнопка Refresh
    with gr.Row():
        show_inactive = gr.Checkbox(label="Show inactive", value=True)
        refresh_button = gr.Button("Refresh")

    # Поле поиска
    with gr.Row():
        search_input = gr.Textbox(label="Search", placeholder="Enter data to filter...", interactive=True)

    # Выбор пользователя
    with gr.Row():
        user_selector = gr.Dropdown(label="Select User", choices=[], interactive=True)
        user_info_display = gr.Textbox(label="User Details", lines=10, interactive=False)

    # Таблица с данными
    with gr.Row():
        stats_table = gr.Dataframe(
            headers=["👤 User", "📊 Used", "📦 Limit", "🌐 IP Address", "⚡ St.", "💳 $", "UID"],
            value=update_table(True),  # Функция возвращает данные для таблицы
            interactive=False,
            wrap=True
        )

    # Функция для обновления таблицы и списка пользователей
    def refresh_table(show_inactive):
        update_traffic_data(USER_DB_PATH)
        table = update_table(show_inactive)
        user_list = table["👤 User"].tolist()
        return "", table, user_list

    # Обновление таблицы при нажатии Refresh
    refresh_button.click(
        fn=refresh_table,
        inputs=[show_inactive],
        outputs=[search_input, stats_table, user_selector]
    )

    # Поиск
    def search_and_update_table(query, show_inactive):
        table = update_table(show_inactive)
        if query:
            table = [row for row in table if query.lower() in " ".join(map(str, row)).lower()]
        user_list = table["👤 User"].tolist()
        return table, user_list

    search_input.change(
        fn=search_and_update_table,
        inputs=[search_input, show_inactive],
        outputs=[stats_table, user_selector]
    )

    # Показ информации о пользователе
    def display_user_info(selected_user):
        if not selected_user:
            return "Please select a user to view details."
        return show_user_info(selected_user)

    user_selector.change(
        fn=display_user_info,
        inputs=[user_selector],
        outputs=[user_info_display]
    )