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
            value="Select a user to view details.",
            elem_id="user-info-block"
        )

    # Таблица с данными пользователей
    with gr.Row():
        stats_table = gr.Dataframe(
            headers=["👤 User", "📊 Used", "📦 Limit", "🌐 IP Address", "⚡ St.", "💳 $", "UID"],
            value=update_table(True),
            interactive=False
        )

    # Обновление данных при нажатии Refresh
    def refresh_table(show_inactive):
        update_traffic_data(USER_RECORDS_PATH)  # Обновление данных трафика
        table = update_table(show_inactive)  # Перезагрузка данных таблицы
        return table, "Select a user to view details."

    refresh_button.click(
        fn=refresh_table,
        inputs=[show_inactive],
        outputs=[stats_table, selected_user_info]
    )

    # Обработка выбора строки в таблице
    def handle_user_selection(row_index):
        print(f"[DEBUG] Row index selected: {row_index}")
        try:
            row_index = int(row_index)  # Преобразование индекса строки в число
            table = update_table(True)  # Загружаем данные таблицы
            selected_row = table.iloc[row_index]  # Извлекаем выбранную строку
            username = selected_row["👤 User"]
            return show_user_info(username, None)  # Форматируем данные пользователя
        except ValueError:
            return "Invalid row selected. Please try again."
        except Exception as e:
            print(f"[DEBUG] Error in handle_user_selection: {e}")
            return f"Error processing data: {str(e)}"

    stats_table.select(
        fn=handle_user_selection,
        inputs=[],
        outputs=[selected_user_info]
    )