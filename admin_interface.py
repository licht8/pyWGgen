import gradio as gr
import os
import json
import subprocess

# Utility functions
def create_user(username):
    """Создание нового пользователя."""
    if not username:
        return "Ошибка: имя пользователя не может быть пустым."
    try:
        subprocess.run(["python3", "main.py", username], check=True)
        return f"✅ Пользователь {username} успешно создан."
    except Exception as e:
        return f"❌ Ошибка при создании пользователя: {str(e)}"

def list_users():
    """Чтение списка пользователей из user_records.json."""
    user_records_path = os.path.join("user", "data", "user_records.json")
    if not os.path.exists(user_records_path):
        return "❌ Файл user_records.json не найден."

    try:
        with open(user_records_path, "r") as f:
            user_data = json.load(f)

        if not user_data:
            return "❌ Нет зарегистрированных пользователей."

        users_list = []
        for username, details in user_data.items():
            user_info = (
                f"👤 Пользователь: {username}\n"
                f"   📅 Создан: {details.get('created_at', 'N/A')}\n"
                f"   ⏳ Истекает: {details.get('expires_at', 'N/A')}\n"
                f"   🌐 Адрес: {details.get('address', 'N/A')}"
            )
            users_list.append(user_info)

        return "\n\n".join(users_list)

    except json.JSONDecodeError:
        return "❌ Ошибка чтения файла user_records.json. Проверьте его формат."

def delete_user(username):
    """Удаление пользователя и его конфигурации."""
    user_records_path = os.path.join("user", "data", "user_records.json")
    user_file = os.path.join("user", "data", f"{username}.conf")

    if not os.path.exists(user_records_path):
        return "❌ Файл user_records.json не найден."

    if not os.path.exists(user_file):
        return f"❌ Пользователь {username} не найден."

    try:
        # Удаляем пользователя из JSON
        with open(user_records_path, "r") as f:
            user_data = json.load(f)

        if username in user_data:
            del user_data[username]
            with open(user_records_path, "w") as f:
                json.dump(user_data, f, indent=4)

        # Удаляем конфигурационный файл
        os.remove(user_file)
        return f"✅ Пользователь {username} успешно удалён."
    except Exception as e:
        return f"❌ Ошибка при удалении пользователя: {str(e)}"

# Gradio interface
with gr.Blocks() as admin_interface:
    gr.Markdown("## Админка для управления WireGuard")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Создать пользователя")
            username_input = gr.Textbox(label="Имя пользователя")
            create_button = gr.Button("Создать")
            create_output = gr.Textbox(label="Результат создания")
            create_button.click(create_user, inputs=username_input, outputs=create_output)

        with gr.Column():
            gr.Markdown("### Список пользователей")
            list_button = gr.Button("Показать пользователей")
            list_output = gr.Textbox(label="Список пользователей", interactive=False)
            list_button.click(list_users, outputs=list_output)

    with gr.Row():
        gr.Markdown("### Удалить пользователя")
        delete_input = gr.Textbox(label="Имя пользователя для удаления")
        delete_button = gr.Button("Удалить")
        delete_output = gr.Textbox(label="Результат удаления")
        delete_button.click(delete_user, inputs=delete_input, outputs=delete_output)

if __name__ == "__main__":
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
