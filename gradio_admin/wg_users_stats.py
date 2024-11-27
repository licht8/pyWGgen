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
    users = pd.DataFrame.from_dict(data, orient="index")
    users.reset_index(inplace=True)
    users.rename(columns={"index": "username"}, inplace=True)  # Преобразуем ключи в столбец "username"
    return users

# Функция для получения списка пользователей
def get_user_list(input_text=""):
    users = load_users()
    if users.empty:
        return ["Нет пользователей"]

    if input_text:
        filtered_usernames = users["username"][users["username"].str.contains(input_text, case=False)].tolist()
        return filtered_usernames if filtered_usernames else ["Нет совпадений"]
    return users["username"].tolist()

# Функция для отображения данных выбранного пользователя
def get_user_details(username):
    if username == "username" or username in ["Нет пользователей", "Нет совпадений"]:
        return pd.DataFrame(), "Выберите пользователя, чтобы увидеть данные."

    users = load_users()
    if users.empty or username not in users["username"].values:
        return pd.DataFrame(), "Пользователь не найден."

    user_data = users[users["username"] == username].transpose()
    user_data.columns = ["Данные"]  # Для удобного отображения в таблице
    user_data.reset_index(inplace=True)
    user_data.rename(columns={"index": "Поле"}, inplace=True)

    return user_data[["Поле", "Данные"]], None

# Функции управления пользователями
def block_unblock_user(username):
    if username == "username" or username in ["Нет пользователей", "Нет совпадений"]:
        return "Выберите корректного пользователя."

    users = load_users()
    if users.empty or username not in users["username"].values:
        return "Пользователь не найден."

    user_status = users.loc[users["username"] == username, "status"].iloc[0]
    new_status = "inactive" if user_status == "active" else "active"
    users.loc[users["username"] == username, "status"] = new_status
    with open(USER_DB_PATH, "w") as file:
        json.dump(users.set_index("username").to_dict(orient="index"), file, indent=4)
    return f"Пользователь {username} {'заблокирован' if new_status == 'inactive' else 'разблокирован'}."

def delete_user(username):
    if username == "username" or username in ["Нет пользователей", "Нет совпадений"]:
        return "Выберите корректного пользователя."

    users = load_users()
    if users.empty or username not in users["username"].values:
        return "Пользователь не найден."

    users = users[users["username"] != username]
    with open(USER_DB_PATH, "w") as file:
        json.dump(users.set_index("username").to_dict(orient="index"), file, indent=4)
    return f"Пользователь {username} удален."

def archive_user(username):
    if username == "username" or username in ["Нет пользователей", "Нет совпадений"]:
        return "Выберите корректного пользователя."

    users = load_users()
    if users.empty or username not in users["username"].values:
        return "Пользователь не найден."

    users.loc[users["username"] == username, "status"] = "archived"
    with open(USER_DB_PATH, "w") as file:
        json.dump(users.set_index("username").to_dict(orient="index"), file, indent=4)
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

        # Поле для поиска пользователя
        user_input = gr.Textbox(placeholder="Введите имя пользователя для поиска", label="Поиск пользователя")

        # Выпадающее меню с пользователями
        user_dropdown = gr.Dropdown(choices=["username"], label="Выберите пользователя")

        # Таблица для отображения данных выбранного пользователя
        user_table = gr.DataFrame(headers=["Поле", "Данные"], interactive=False, label="Данные пользователя")

        # Кнопки для управления пользователем
        with gr.Row():
            block_button = gr.Button("Block/Unblock")
            delete_button = gr.Button("Удалить")
            archive_button = gr.Button("Архивировать")

        # Вывод сообщений
        action_output = gr.Textbox(label="Результат действия", interactive=False)

        # Логика обновления Dropdown при поиске
        def update_dropdown(input_text):
            return gr.Dropdown.update(choices=get_user_list(input_text))

        user_input.change(update_dropdown, inputs=user_input, outputs=user_dropdown)

        # Логика выбора пользователя
        user_dropdown.change(get_user_details, inputs=user_dropdown, outputs=[user_table, action_output])

        # Логика кнопок управления
        block_button.click(block_unblock_user, inputs=user_dropdown, outputs=action_output)
        delete_button.click(delete_user, inputs=user_dropdown, outputs=action_output)
        archive_button.click(archive_user, inputs=user_dropdown, outputs=action_output)

    return tab
