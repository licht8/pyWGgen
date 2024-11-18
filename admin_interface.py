import gradio as gr
import os
import subprocess

# Utility functions
def create_user(username):
    if not username:
        return "Ошибка: имя пользователя не может быть пустым."
    try:
        subprocess.run(["python3", "main.py", username], check=True)
        return f"✅ Пользователь {username} успешно создан."
    except Exception as e:
        return f"❌ Ошибка при создании пользователя: {str(e)}"

def list_users():
    user_dir = os.path.join("user", "data")
    if not os.path.exists(user_dir):
        return "❌ Папка с пользователями не найдена."
    users = os.listdir(user_dir)
    if not users:
        return "❌ Нет зарегистрированных пользователей."
    return "\n".join(users)

def delete_user(username):
    user_file = os.path.join("user", "data", f"{username}.conf")
    if not os.path.exists(user_file):
        return f"❌ Пользователь {username} не найден."
    try:
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
            list_output = gr.Textbox(label="Список пользователей")
            list_button.click(list_users, outputs=list_output)

    with gr.Row():
        gr.Markdown("### Удалить пользователя")
        delete_input = gr.Textbox(label="Имя пользователя для удаления")
        delete_button = gr.Button("Удалить")
        delete_output = gr.Textbox(label="Результат удаления")
        delete_button.click(delete_user, inputs=delete_input, outputs=delete_output)

if __name__ == "__main__":
    admin_interface.launch()
