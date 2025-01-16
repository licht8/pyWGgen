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
from settings import QR_CODE_DIR

def statistics_tab():
    """Создает вкладку статистики пользователей WireGuard."""
    # Получение начальных данных
    def get_initial_data():
        update_traffic_data(USER_DB_PATH)
        table = update_table(True)
        user_list = ["Select a user"] + table["👤 User"].tolist() if not table.empty else ["Select a user"]
        return table, user_list

    initial_table, initial_user_list = get_initial_data()

    with gr.Row():
        gr.Markdown("## Statistics")

    # Чекбокс Show inactive и кнопка Refresh
    with gr.Row():
        show_inactive = gr.Checkbox(label="Show inactive", value=True)
        refresh_button = gr.Button("Refresh")

    # Поле поиска
    with gr.Row():
        search_input = gr.Textbox(label="Search", placeholder="Enter text to filter table...", interactive=True)

    # Выбор пользователя и отображение информации и QR-кода
    with gr.Row(equal_height=True):  # Устанавливаем одинаковую высоту
        with gr.Column(scale=3):  # Левая колонка для User Details
            user_selector = gr.Dropdown(
                label="Select User",
                choices=initial_user_list,
                value="Select a user",
                interactive=True
            )
            user_info_display = gr.Textbox(
                label="User Details",
                value="",
                lines=10,
                interactive=False
            )
        with gr.Column(scale=1, min_width=200):  # Правая колонка для QR-кода
            qr_code_display = gr.Image(
                label="User QR Code",
                type="filepath",
                interactive=False,
                height=200  # Делаем высоту фиксированной для пропорционального вида
            )

    # Таблица с данными
    with gr.Row():
        stats_table = gr.Dataframe(
            headers=["👤 User", "📊 Used", "📦 Limit", "🌐 IP Address", "⚡ St.", "💳 $", "UID"],
            value=initial_table,
            interactive=False,
            wrap=True
        )

    # Функция для обновления таблицы и сброса данных
    def refresh_table(show_inactive):
        update_traffic_data(USER_DB_PATH)
        table = update_table(show_inactive)
        if table.empty:
            print("[DEBUG] Table is empty after update.")
        else:
            print(f"[DEBUG] Updated table:\n{table}")
        user_list = ["Select a user"] + table["👤 User"].tolist() if not table.empty else ["Select a user"]
        print(f"[DEBUG] User list: {user_list}")
        # Сбрасываем user_info_display, user_selector и qr_code_display
        return "", table, gr.update(choices=user_list, value="Select a user"), "", None

    # Обновление таблицы при нажатии Refresh
    refresh_button.click(
        fn=refresh_table,
        inputs=[show_inactive],
        outputs=[search_input, stats_table, user_selector, user_info_display, qr_code_display]
    )

    # Функция для поиска по таблице
    def search_table(query):
        table = update_table(True)  # Загружаем оригинальную таблицу
        if query:
            # Фильтруем таблицу по всем колонкам
            filtered_table = table.loc[
                table.apply(lambda row: query.lower() in " ".join(map(str, row)).lower(), axis=1)
            ]
            print(f"[DEBUG] Filtered table:\n{filtered_table}")
            return filtered_table
        return table  # Если запрос пуст, возвращаем оригинальную таблицу

    # Поиск по таблице
    search_input.change(
        fn=search_table,
        inputs=[search_input],
        outputs=[stats_table]
    )

    # Функция для поиска QR-кода пользователя
    def find_qr_code(username):
        """
        Находит путь к QR-коду пользователя.
        :param username: Имя пользователя
        :return: Путь к файлу QR-кода или None, если файл не найден.
        """
        qr_code_file = QR_CODE_DIR / f"{username}.png"
        if qr_code_file.exists():
            return str(qr_code_file)
        return None

    # Показ информации о пользователе и его QR-кода
    def display_user_info(selected_user):
        # Убедимся, что selected_user — это строка, а не список
        if isinstance(selected_user, list):
            if len(selected_user) > 0:
                selected_user = selected_user[0]
            else:
                selected_user = "Select a user"

        # Если выбран "Select a user", возвращаем пустую строку и пустой QR-код
        if not selected_user or selected_user == "Select a user":
            return "", None

        # Получение информации о пользователе
        user_info = show_user_info(selected_user)
        qr_code_path = find_qr_code(selected_user)
        print(f"[DEBUG] User info:\n{user_info}")
        print(f"[DEBUG] QR Code path for {selected_user}: {qr_code_path}")
        return user_info, qr_code_path

    user_selector.change(
        fn=display_user_info,
        inputs=[user_selector],
        outputs=[user_info_display, qr_code_display]
    )