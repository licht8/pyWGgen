#!/usr/bin/env python3
# statistics_tab.py
# Вкладка "Statistics" Gradio-интерфейса wg_qr_generator

import gradio as gr
import pandas as pd
import json
import os
from settings import USER_DB_PATH  # Путь к JSON с данными пользователей


def load_user_records():
    """Загружает данные пользователей из JSON."""
    print("[DEBUG] Загрузка данных пользователей из JSON...")
    if not os.path.exists(USER_DB_PATH):
        print("[ERROR] Файл JSON с пользователями не найден!")
        return {}

    with open(USER_DB_PATH, "r") as f:
        data = json.load(f)
    print(f"[DEBUG] Загружено {len(data)} пользователей.")
    return data


def prepare_table_data(show_inactive=True):
    """Создает данные для таблицы."""
    print(f"[DEBUG] Подготовка данных для таблицы. Show inactive: {show_inactive}")
    user_records = load_user_records()
    table_data = []

    for user in user_records.values():
        if not show_inactive and user.get("status") != "active":
            continue
        table_data.append({
            "Select": False,
            "User": user.get("username", "N/A"),
            "Used": user.get("data_used", "0.0 KiB"),
            "Limit": user.get("data_limit", "100.0 GB"),
            "Status": user.get("status", "inactive"),
            "Price": user.get("subscription_price", "0.00 USD"),
            "UID": user.get("user_id", "N/A")
        })

    print(f"[DEBUG] Подготовлено {len(table_data)} записей для таблицы.")
    return pd.DataFrame(table_data)


def get_selected_user(dataframe):
    """Возвращает выбранного пользователя из таблицы."""
    print(f"[DEBUG] Получены данные из таблицы: {dataframe}")
    selected_rows = dataframe[dataframe["Select"] == True]
    if selected_rows.empty:
        print("[WARNING] Пользователь не выбран.")
        return "No user selected"
    selected_user = selected_rows.iloc[0]
    print(f"[DEBUG] Выбран пользователь: {selected_user['User']} (UID: {selected_user['UID']})")
    return selected_user["UID"]


def get_user_info(user_id):
    """Возвращает подробную информацию о пользователе."""
    print(f"[DEBUG] Запрос информации о пользователе с UID: {user_id}")
    if user_id == "No user selected" or not user_id:
        print("[WARNING] Пользователь не выбран.")
        return "No user selected"
    user_records = load_user_records()
    for user in user_records.values():
        if user.get("user_id") == user_id:
            print(f"[DEBUG] Найден пользователь: {user.get('username')}")
            return json.dumps(user, indent=4)
    print("[WARNING] Пользователь не найден.")
    return "User not found."


def statistics_tab():
    """Создает интерфейс вкладки статистики."""
    with gr.Tab("🔍 Statistics"):
        gr.Markdown("## Статистика пользователей")

        # Фильтры
        with gr.Row():
            search_box = gr.Textbox(label="Search", placeholder="Search for users...")
            show_inactive_checkbox = gr.Checkbox(label="Show inactive users", value=True)
            refresh_button = gr.Button("Refresh Table")

        # Таблица данных
        user_table = gr.Dataframe(
            value=prepare_table_data(),
            interactive=True,
            label="Users Table"
        )

        # Подробная информация
        user_info_box = gr.Textbox(label="User Information", lines=10, interactive=False)

        # Управление пользователями
        with gr.Row():
            block_button = gr.Button("Block User")
            delete_button = gr.Button("Delete User")

        # Связывание компонентов
        def filter_table(search_query, show_inactive):
            print(f"[DEBUG] Фильтрация таблицы. Query: '{search_query}', Show inactive: {show_inactive}")
            df = prepare_table_data(show_inactive)
            if search_query:
                df = df[df.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)]
            print(f"[DEBUG] Фильтр применен. Найдено записей: {len(df)}.")
            return df

        refresh_button.click(lambda: prepare_table_data(), outputs=user_table)
        search_box.change(lambda q, show: filter_table(q, show), inputs=[search_box, show_inactive_checkbox], outputs=user_table)
        show_inactive_checkbox.change(lambda q, show: filter_table(q, show), inputs=[search_box, show_inactive_checkbox], outputs=user_table)
        user_table.change(get_selected_user, inputs=user_table, outputs=user_info_box)
        block_button.click(get_user_info, inputs=user_table, outputs=user_info_box)
        delete_button.click(get_user_info, inputs=user_table, outputs=user_info_box)
