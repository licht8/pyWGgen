import os
import json
import pandas as pd
import gradio as gr
from datetime import datetime
from settings import USER_DB_PATH

# Словарь эмодзи для полей
FIELD_EMOJIS = {
    "username": "👤",
    "group": "🛡️",
    "status": "⚡",
    "created_at": "📅",
    "expires_at": "⏳",
    "auto_suspend_date": "🛑",
    "allowed_ips": "🌐",
    "dns_custom": "📡",
    "public_key": "🔑",
    "email": "📧",
    "telegram_id": "📲",
    "subscription_plan": "💳",
    "data_used": "📊",
    "admin_notes": "📝",
    "preferred_language": "🌍",
    "last_handshake": "🤝",
    "total_transfer": "🚀",
    # Добавьте сюда другие поля, если нужно
}

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

    # Добавляем эмодзи в отдельный столбец
    user_data["Эмодзи"] = user_data.index.map(FIELD_EMOJIS.get)
    user_data.reset_index(inplace=True)
    user_data.rename(columns={"index": "Поле"}, inplace=True)

    return user_data[["Эмодзи", "Поле", "Данные"]], None

# Функции управления пользователями
def block_unblock_user(username):
    users = load_users()
    if users.empty or username not in users["username"].values:
        return "Пользователь не найден."

    user_status = users.loc[users["username"] == username, "status"].iloc[0]
    new_status = "inactive" if user_status == "active" else "active"
    users.loc[users["username"] == username, "status"] = new_status
    save_users(users)
    return f"Пользователь {username} {'заблокирован' if new_status == 'inactive' else 'разблокирован'}."

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
            overflow: auto; 
            max-width: 100%;
            word-wrap: break-word;
            white-space: nowrap;
        }
        .gr-table-container th, .gr-table-container td {
            max-width: 200px; 
            overflow: hidden; 
            text-overflow: ellipsis;
        }
    """) as tab:
        gr.Markdown("# Управление пользователями")

        # Выпадающее меню для выбора пользователя
        users = load_users()
        user_dropdown = gr.Dropdown(
            choices=users["username"].tolist() if not users.empty else [],
            label="Выберите пользователя",
        )

        # Таблица для отображения данных выбранного пользователя
        user_table = gr.DataFrame(
            headers=["Эмодзи", "Поле", "Данные"],
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

        # Логика кнопок и выпадающего меню
        user_dropdown.change(
            get_user_details, inputs=user_dropdown, outputs=[user_table, action_output]
        )
        block_button.click(
            block_unblock_user, inputs=user_dropdown, outputs=action_output
        )
        delete_button.click(delete_user, inputs=user_dropdown, outputs=action_output)
        archive_button.click(archive_user, inputs=user_dropdown, outputs=action_output)

    return tab
