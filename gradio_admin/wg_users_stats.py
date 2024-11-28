import os
import json
import pandas as pd
import gradio as gr
from settings import USER_DB_PATH

# Функция загрузки данных из JSON
def load_users():
    if not os.path.exists(USER_DB_PATH):
        return pd.DataFrame()
    try:
        with open(USER_DB_PATH, "r") as file:
            data = json.load(file)
        users = pd.DataFrame.from_dict(data, orient="index")
        users.reset_index(inplace=True)
        users.rename(columns={"index": "username"}, inplace=True)
        return users
    except json.JSONDecodeError:
        return pd.DataFrame()

# Функция фильтрации пользователей
def filter_users(search_text):
    users = load_users()
    if users.empty:
        return ["Нет доступных пользователей"]

    filtered_users = users["username"][users["username"].str.contains(search_text, case=False)].tolist()
    return filtered_users if filtered_users else ["Нет совпадений"]

# Функция для отображения данных выбранного пользователя
def get_user_details(username):
    users = load_users()
    if username in ["Нет доступных пользователей", "Нет совпадений"]:
        return pd.DataFrame(), "Пользователь не найден."

    if username not in users["username"].values:
        return pd.DataFrame(), "Пользователь не найден."

    user_data = users[users["username"] == username].transpose()
    user_data.columns = ["Данные"]
    user_data.reset_index(inplace=True)
    user_data.rename(columns={"index": "Поле"}, inplace=True)
    return user_data[["Поле", "Данные"]], None

# Функции управления пользователями
def block_unblock_user(username):
    users = load_users()
    if username not in users["username"].values:
        return "Пользователь не найден."

    current_status = users.loc[users["username"] == username, "status"].iloc[0]
    new_status = "inactive" if current_status == "active" else "active"
    users.loc[users["username"] == username, "status"] = new_status

    # Сохранение изменений
    data = users.set_index("username").to_dict(orient="index")
    with open(USER_DB_PATH, "w") as file:
        json.dump(data, file, indent=4)

    return f"Пользователь {username} {'заблокирован' if new_status == 'inactive' else 'разблокирован'}."

def delete_user(username):
    users = load_users()
    if username not in users["username"].values:
        return "Пользователь не найден."

    users = users[users["username"] != username]
    data = users.set_index("username").to_dict(orient="index")
    with open(USER_DB_PATH, "w") as file:
        json.dump(data, file, indent=4)

    return f"Пользователь {username} удален."

def archive_user(username):
    users = load_users()
    if username not in users["username"].values:
        return "Пользователь не найден."

    users.loc[users["username"] == username, "status"] = "archived"
    data = users.set_index("username").to_dict(orient="index")
    with open(USER_DB_PATH, "w") as file:
        json.dump(data, file, indent=4)

    return f"Пользователь {username} архивирован."

# Интерфейс вкладки
def statistics_tab():
    with gr.Blocks() as tab:
        gr.Markdown("# Управление пользователями")

        # Поле поиска пользователей
        search_input = gr.Textbox(
            placeholder="Введите имя пользователя для поиска", label="Поиск пользователя"
        )

        # Выпадающее меню для выбора пользователя
        users = load_users()
        user_dropdown = gr.Dropdown(
            choices=users["username"].tolist() if not users.empty else ["Нет доступных пользователей"],
            label="Выберите пользователя"
        )

        # Таблица с данными выбранного пользователя
        user_table = gr.DataFrame(headers=["Поле", "Данные"], label="Данные пользователя")

        # Кнопки управления пользователем
        with gr.Row():
            block_button = gr.Button("Block/Unblock")
            delete_button = gr.Button("Удалить")
            archive_button = gr.Button("Архивировать")

        # Поле вывода результата
        action_output = gr.Textbox(label="Результат действия", interactive=False)

        # Логика фильтрации пользователей
        def update_user_list(search_text):
            filtered_choices = filter_users(search_text)
            return gr.Dropdown.update(choices=filtered_choices)

        search_input.change(update_user_list, inputs=search_input, outputs=user_dropdown)

        # Логика выбора пользователя
        user_dropdown.change(get_user_details, inputs=user_dropdown, outputs=[user_table, action_output])

        # Логика управления пользователем
        block_button.click(block_unblock_user, inputs=user_dropdown, outputs=action_output)
        delete_button.click(delete_user, inputs=user_dropdown, outputs=action_output)
        archive_button.click(archive_user, inputs=user_dropdown, outputs=action_output)

    return tab
