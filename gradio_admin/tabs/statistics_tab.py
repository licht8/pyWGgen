# gradio_admin/tabs/statistics_tab.py
# Вкладка "Statistics" для Gradio-интерфейса проекта wg_qr_generator

import gradio as gr # type: ignore
import pandas as pd # type: ignore
from gradio_admin.functions.user_records import load_user_records
from gradio_admin.functions.format_helpers import format_time
from gradio_admin.functions.table_helpers import update_table
from gradio_admin.functions.format_helpers import format_user_info
from gradio_admin.functions.user_records import load_user_records
from modules.traffic_updater import update_traffic_data
from settings import USER_DB_PATH

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
            headers=["👤 User", "📊 Used", "📦 Limit", "🌐 IP Address", "⚡ St.", "💳 $", "UID"],  # Обновлено
            value=update_table(True),
            interactive=False,  # Таблица только для чтения
            wrap=True
        )

    # Функция для показа информации о пользователе
    def show_user_info(selected_data, query):
        """Показывает подробную информацию о выбранном пользователе."""
        print("[DEBUG] Вызов функции show_user_info")  # Отладка
        print(f"[DEBUG] Query: {query}")  # Отладка

        if not query.strip():
            return "Please enter a query to filter user data and then click a cell to view user details and perform actions."

        if selected_data is None or len(selected_data) == 0:
            return "Select a row from the table!"

        try:
            row = selected_data if isinstance(selected_data, list) else selected_data.iloc[0].values
            username = row[0].replace("👤 User account : ", "") if len(row) > 0 else "N/A"
            records = load_user_records()
            user_data = records.get(username, {})

            created = user_data.get("created_at", "N/A")
            expires = user_data.get("expires_at", "N/A")
            int_ip = user_data.get("address", "N/A")

            user_info = f"""
    👤 User: {username}
    📧 Email: user@mail.wg
    🌱 Created: {format_time(created)}
    🔥 Expires: {format_time(expires)}
    🌐 Internal IP: {int_ip}
    """
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
        update_traffic_data(USER_DB_PATH)  # Обновление трафика пользователей
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
