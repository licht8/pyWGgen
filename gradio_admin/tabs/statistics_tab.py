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
    """Создаёт вкладку статистики пользователей WireGuard."""
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
            value="Select a user to view details."
        )

    # Таблица с данными пользователей
    with gr.Row():
        stats_table = gr.Dataframe(
            headers=["👤 User", "📊 Used", "📦 Limit", "🌐 IP Address", "⚡ St.", "💳 $", "UID"],
            value=update_table(True).values.tolist(),  # Преобразуем в список списков
            interactive=False  # Таблица только для чтения
        )

    # Функция для обработки выбора строки
    def handle_user_selection(selected_data):
        """Обрабатывает выбор строки в таблице."""
        print(f"[DEBUG] Selected data: {selected_data}")  # Отладка

        if selected_data is None:
            return "No row selected. Please select a row from the table!"

        try:
            # Извлекаем данные строки
            username = selected_data[0]  # Извлекаем имя пользователя из первой ячейки строки
            print(f"[DEBUG] Extracted username: {username}")
            return show_user_info(username)  # Форматируем данные пользователя
        except Exception as e:
            print(f"[DEBUG] Error in handle_user_selection: {e}")  # Отладка
            return f"Error processing data: {str(e)}"


    # Привязка выбора строки к отображению данных
    stats_table.select(
        fn=handle_user_selection,
        inputs=None,  # Убираем входные параметры
        outputs=[selected_user_info]
    )

    # Обновление таблицы при нажатии Refresh
    def refresh_table(show_inactive):
        update_traffic_data(USER_DB_PATH)  # Обновляем данные
        return update_table(show_inactive).values.tolist(), "Select a user to view details."

    refresh_button.click(
        fn=refresh_table,
        inputs=[show_inactive],
        outputs=[stats_table, selected_user_info]
    )

    return gr.Blocks()