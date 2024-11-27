import os
import json
import pandas as pd
import gradio as gr
from datetime import datetime
from settings import USER_DB_PATH

# Функция загрузки данных из JSON
def load_users():
    try:
        if not os.path.exists(USER_DB_PATH):
            return pd.DataFrame()
        with open(USER_DB_PATH, "r") as file:
            data = json.load(file)
        users = pd.DataFrame.from_dict(data, orient="index")
        users.reset_index(inplace=True)
        users.rename(columns={"index": "username"}, inplace=True)  # Преобразуем ключи в столбец "username"
        return users
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame()

# Функция сохранения данных в JSON
def save_users(users):
    data = users.set_index("username").to_dict(orient="index")
    with open(USER_DB_PATH, "w") as file:
        json.dump(data, file, indent=4)

# Функция для отображения данных выбранного пользователя
def get_user_details(username):
    users = load_users()
    if users.empty or username not in users["username"].values:
        return pd.DataFrame(), "Пользователь не найден."

    user_data = users[users["username"] == username].transpose()
    user_data.columns = ["Данные"]  # Для удобного отображения в таблице
    user_data.reset_index(inplace=True)
    user_data.rename(columns={"index": "Поле"}, inplace=True)

    return user_data[["Поле", "Данные"]], None

# Функция для фильтрации пользователей
def filter_users(search_text):
    users = load_users()
    if users.empty:
        return ["Нет доступных пользователей"]

    filtered_users = users["username"][users["username"].str.contains(search_text, case=False)].tolist()
    return filtered_users if filtered_users else ["Нет совпадений"]

# Функции управления пользователями
def block_unblock_user(username):
    users = load_users()
    if users.empty or username not in users["username"].values:
        return "Пользователь не найден."

    user_status = users.loc[users["username"] == username, "status"].iloc[0]
    new_status = "inactive" if user_status == "active" else "active"
    users.loc[users["username"] == username, "status"] = new_status
    save_users(users)
    return f"Пользователь {username} {'заблокирован' if new_status == "inactive" else "разблокирован"}."

def delete_user(username):
    users = load_users()
    if users.empty or username not in users["username"].values:
        return "Пользователь не найден."

    users = users[users["username"] != username]
    save_users(users)
    return f"Пользователь {username} удален."

def archive_user(username):
    users = load_users()
    if users.empty or username not in users["username"].values:
        return "Пользователь не найден."

    users.loc[users["username"] == username, "status"] = "archived"
    save_users(users)
    return f"Пользователь {username} архивирован."

# Интерфейс вкладки
def statistics_tab():
    with gr.Blocks(css="""
        .gr-table-container { 
            overflow-x: auto; 
            max-width: 100%; 
            word-wrap: break-word;
            white-space: nowrap;
        }
        .gr-table-container th, .gr-table-container td {
            max-width: 300px; 
            overflow: hidden; 
            text-overflow: ellipsis;
            padding: 10px 5px;
        }
        @media screen and (max-width: 600px) {
            .gr-table-container th, .gr-table-container td {
                font-size: 12px;
                max-width: 150px;
            }
        }
    """) as tab:
        gr.Markdown("# Управление пользователями")

        # Поле для фильтрации списка пользователей
        search_input = gr.Textbox(placeholder="Введите имя пользователя для поиска", label="Поиск пользователя")

        # Выпадающее меню для выбора пользователя
        users = load_users()
        user_dropdown = gr.Dropdown(
            choices=users["username"].tolist() if not users.empty else ["Нет доступных пользователей"],
            label="Выберите пользователя",
        )

        # Таблица для отображения данных выбранного пользователя
        user_table = gr.DataFrame(
            headers=["Поле", "Данные"],
            interactive=False,
            label="Данные пользователя"
        )

        # Кнопки для управления пользователем
        with gr.Row():
            block_button = gr.Button("Block/Unblock")
            delete_button = gr.Button("Удалить")
            archive_button = gr.Button("Архивировать")

        # Вывод сообщений
        action_output = gr.Textbox(label="Результат действия", interactive=False)

        # Логика обновления Dropdown при поиске
        search_input.change(
            filter_users, inputs=search_input, outputs=user_dropdown
        )

        # Логика кнопок и выбора пользователя
        user_dropdown.change(
            get_user_details, inputs=user_dropdown, outputs=[user_table, action_output]
        )
        block_button.click(
            block_unblock_user, inputs=user_dropdown, outputs=action_output
        )
        delete_button.click(delete_user, inputs=user_dropdown, outputs=action_output)
        archive_button.click(archive_user, inputs=user_dropdown, outputs=action_output)

    return tab
