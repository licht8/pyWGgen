import os
import json
import pandas as pd
import gradio as gr
from datetime import datetime
from settings import USER_DB_PATH

# Функция загрузки данных из JSON
def load_users():
    if not os.path.exists(USER_DB_PATH):
        return pd.DataFrame()
    with open(USER_DB_PATH, "r") as file:
        data = json.load(file)
    # Преобразуем JSON в DataFrame
    users = pd.DataFrame.from_dict(data, orient="index")
    users.reset_index(inplace=True)
    users.rename(columns={"index": "username"}, inplace=True)  # Преобразуем ключи в столбец "username"
    return users

# Функция сохранения данных в JSON
def save_users(users):
    data = users.set_index("username").to_dict(orient="index")
    with open(USER_DB_PATH, "w") as file:
        json.dump(data, file, indent=4)

# Генерация статистики
def generate_statistics():
    users = load_users()
    if users.empty:
        return "Нет данных для отображения статистики."
    
    total_users = len(users)
    active_users = len(users[users["status"] == "active"])
    inactive_users = len(users[users["status"] == "inactive"])
    expired_users = len(users[pd.to_datetime(users["expires_at"]) < datetime.now()])
    total_data_used = users["data_used"].str.replace(" KiB", "").astype(float).sum()
    
    stats = f"""
    **Общая статистика пользователей:**
    - Всего пользователей: {total_users}
    - Активных пользователей: {active_users}
    - Неактивных пользователей: {inactive_users}
    - Просроченных пользователей: {expired_users}
    - Общее потребление данных: {total_data_used:.2f} KiB
    """
    return stats

# Функция фильтрации пользователей
def filter_users(group, status, sort_by):
    users = load_users()
    if users.empty:
        return pd.DataFrame(), []

    # Применяем фильтры
    if group != "Все":
        users = users[users["group"] == group]
    if status != "Все":
        users = users[users["status"] == status]
    if sort_by:
        users = users.sort_values(by=sort_by)
    
    filtered_usernames = users["username"].tolist()  # Для выбора в CheckboxGroup
    display_users = users[["username", "group", "status", "created_at", "expires_at"]]
    return display_users, filtered_usernames

# Удаление пользователей
def delete_selected_users(selected_usernames):
    users = load_users()
    if users.empty or not selected_usernames:
        return "Нет данных для удаления."

    users = users[~users["username"].isin(selected_usernames)]
    save_users(users)
    return f"Удалено пользователей: {len(selected_usernames)}"

# Интерфейс вкладки статистики
def statistics_tab():
    with gr.Blocks() as tab:
        gr.Markdown("# Вкладка: Статистика и управление пользователями")

        # Фильтры
        with gr.Row():
            group = gr.Dropdown(["Все", "admin", "guest"], label="Группа", value="Все")
            status = gr.Dropdown(["Все", "active", "inactive"], label="Статус", value="Все")
            sort_by = gr.Dropdown(
                [None, "username", "created_at", "expires_at"],
                label="Сортировать по",
                value=None,
            )
            filter_button = gr.Button("Применить фильтры")

        # Вывод таблицы и чекбоксы
        user_table = gr.DataFrame(label="Список пользователей", interactive=False)
        selected_users = gr.CheckboxGroup(label="Выберите пользователей для удаления")

        # Удаление и статистика
        with gr.Row():
            delete_button = gr.Button("Удалить выбранных пользователей")
        gr.Markdown("## Общая статистика пользователей")
        stats_output = gr.Textbox(label="Статистика", interactive=False)

        # Логика кнопок
        filter_button.click(
            filter_users, 
            inputs=[group, status, sort_by], 
            outputs=[user_table, selected_users]
        )
        delete_button.click(
            delete_selected_users, 
            inputs=[selected_users], 
            outputs=stats_output
        )
        stats_output.change(generate_statistics, inputs=None, outputs=stats_output)

    return tab
