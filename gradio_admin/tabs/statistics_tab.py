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

    # Область для отображения информации о выбранном пользователе
    with gr.Row():
        selected_user_info = gr.Textbox(
            label="User Information", 
            interactive=False, 
            value="Select a user to view details.",
            elem_id="user-info-block"
        )

    # Поле поиска
    with gr.Row():
        search_input = gr.Textbox(label="Search", placeholder="Enter data to filter...", interactive=True)

    # Таблица с данными
    with gr.Row():
        stats_table = gr.Dataframe(
            headers=["👤 User", "📊 Used", "📦 Limit", "🌐 IP Address", "⚡ St.", "💳 $", "UID"],
            value=update_table(True),  # Функция возвращает данные для таблицы
            interactive=False,  # Таблица только для чтения
            wrap=True
        )

    # Функция для отображения информации о пользователе
    def handle_user_selection(row_index, query=None):
        print(f"[DEBUG] Raw row_index: {row_index}")  # Отладка
        try:
            row_index = int(row_index)  # Преобразование в число
            print(f"[DEBUG] Parsed row_index: {row_index}")  # Отладка

            if row_index < 0:
                return "Select a valid row from the table!"
            
            # Получаем данные таблицы
            table = update_table(True)
            selected_row = table[row_index]  # Извлекаем выбранную строку
            username = selected_row[0].strip().lower()  # Извлекаем имя пользователя
            print(f"[DEBUG] Extracted username: {username}")
            return show_user_info(username, query)
        except ValueError:
            print(f"[DEBUG] ValueError for row_index: {row_index}")  # Отладка
            return "Invalid row index. Please try again."
        except Exception as e:
            print(f"[DEBUG] Error: {e}")  # Отладка
            return f"Error processing data: {str(e)}"


    # Привязка выбора строки к отображению данных
    stats_table.select(
        fn=handle_user_selection,
        inputs=[search_input],  # Передаём только search_input
        outputs=[selected_user_info]
    )

    # Обновление таблицы при нажатии Refresh
    def refresh_table(show_inactive):
        update_traffic_data(USER_DB_PATH)
        return "", update_table(show_inactive)

    refresh_button.click(
        fn=refresh_table,
        inputs=[show_inactive],
        outputs=[search_input, stats_table]
    )

    # Поиск
    def search_and_update_table(query, show_inactive):
        table = update_table(show_inactive)
        if query:
            table = [row for row in table if query.lower() in " ".join(map(str, row)).lower()]
        return table

    search_input.change(
        fn=search_and_update_table,
        inputs=[search_input, show_inactive],
        outputs=[stats_table]
    )