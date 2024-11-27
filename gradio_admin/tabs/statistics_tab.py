#!/usr/bin/env python3
# statistics_tab.py
# Болванка для вкладки "Statistics" Gradio-интерфейса wg_qr_generator

import gradio as gr
import pandas as pd
import json

# Путь к файлу с данными пользователей
USER_DB_PATH = "user/data/user_records.json"

# Загрузка данных из JSON
def load_user_data():
    with open(USER_DB_PATH, "r") as f:
        data = json.load(f)
    # Преобразование данных для pandas DataFrame
    users = []
    for user in data.values():
        users.append({
            "username": user.get("username"),
            "data_used": user.get("data_used"),
            "data_limit": user.get("data_limit"),
            "status": user.get("status"),
            "subscription_price": user.get("subscription_price")
        })
    return pd.DataFrame(users)

# Функция для отображения подробной информации о пользователе
def get_user_info(username):
    with open(USER_DB_PATH, "r") as f:
        data = json.load(f)
    user_info = data.get(username, {})
    return json.dumps(user_info, indent=4) if user_info else "User not found."

# Функция для фильтрации данных
def filter_users(search_query, show_inactive):
    df = load_user_data()
    if search_query:
        df = df[df.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
    if not show_inactive:
        df = df[df["status"] != "inactive"]
    return df

# Функция блокировки пользователя
def block_user(username):
    with open(USER_DB_PATH, "r") as f:
        data = json.load(f)
    if username in data:
        data[username]["status"] = "blocked"
        with open(USER_DB_PATH, "w") as f:
            json.dump(data, f, indent=4)
        return f"User {username} blocked."
    return "User not found."

# Функция удаления пользователя
def delete_user(username):
    with open(USER_DB_PATH, "r") as f:
        data = json.load(f)
    if username in data:
        del data[username]
        with open(USER_DB_PATH, "w") as f:
            json.dump(data, f, indent=4)
        return f"User {username} deleted."
    return "User not found."

# Интерфейс Gradio
def create_statistics_tab():
    with gr.Blocks() as statistics_tab:
        gr.Markdown("## Статистика пользователей")
        gr.Markdown("Управляйте данными пользователей, фильтруйте и просматривайте подробную информацию.")

        with gr.Row():
            search_box = gr.Textbox(label="Search", placeholder="Search for users...")
            show_inactive_checkbox = gr.Checkbox(label="Show inactive users", value=True)
            refresh_button = gr.Button("Refresh Table")

        with gr.Row():
            user_table = gr.Dataframe(load_user_data(), label="Users Table", interactive=False)
        
        with gr.Row():
            gr.Markdown("### Подробная информация о пользователе")
            user_info_box = gr.Textbox(label="User Information", lines=10, interactive=False)

        with gr.Row():
            selected_user = gr.Textbox(label="Selected User", interactive=False)
            block_button = gr.Button("Block User")
            delete_button = gr.Button("Delete User")

        # Связывание компонентов
        refresh_button.click(lambda: load_user_data(), outputs=user_table)
        search_box.change(lambda q, show: filter_users(q, show), inputs=[search_box, show_inactive_checkbox], outputs=user_table)
        show_inactive_checkbox.change(lambda q, show: filter_users(q, show), inputs=[search_box, show_inactive_checkbox], outputs=user_table)
        user_table.select(lambda idx: get_user_info(user_table.value.iloc[idx]["username"]), outputs=user_info_box)
        block_button.click(block_user, inputs=selected_user, outputs=user_info_box)
        delete_button.click(delete_user, inputs=selected_user, outputs=user_info_box)

    return statistics_tab

# Запуск интерфейса
if __name__ == "__main__":
    with gr.Blocks() as demo:
        with gr.Tab("Статистика"):
            create_statistics_tab()
        demo.launch()
