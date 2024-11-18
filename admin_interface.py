import gradio as gr
import os
import json
import subprocess
from datetime import datetime

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
    """Ручное удаление пользователя с обработкой ошибок."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    user_records_path = os.path.join(base_dir, "user", "data", "user_records.json")
    stale_records_path = os.path.join(base_dir, "user", "stale_user_records.json")
    user_file = os.path.join(base_dir, "user", "data", f"{username}.conf")
    stale_config_dir = os.path.join(base_dir, "user", "stale_config")
    ip_records_path = os.path.join(base_dir, "user", "data", "ip_records.json")
    wg_config_path = os.path.join(base_dir, "user", "data", "wg_configs/wg0.conf")  # Указываем точное имя файла

    print(f"=== Удаление пользователя {username} ===")

    if not os.path.exists(user_records_path):
        print("❌ Файл user_records.json не найден.")
        return "❌ Файл user_records.json не найден."

    try:
        # Читаем записи о пользователях
        print("📂 Чтение user_records.json...")
        with open(user_records_path, "r") as f:
            user_data = json.load(f)

        if username not in user_data:
            print(f"❌ Пользователь {username} не найден в user_records.json.")
            return f"❌ Пользователь {username} не найден в user_records.json."

        # Читаем IP-адреса
        print("📂 Чтение ip_records.json...")
        with open(ip_records_path, "r") as f:
            ip_data = json.load(f)

        # Читаем записи об устаревших пользователях
        print("📂 Чтение stale_user_records.json...")
        if os.path.exists(stale_records_path):
            with open(stale_records_path, "r") as f:
                stale_data = json.load(f)
        else:
            stale_data = {}

        # Переносим данные в архив
        print(f"📦 Перемещение данных пользователя {username} в архив...")
        user_info = user_data.pop(username)
        user_info["removed_at"] = datetime.now().isoformat()
        stale_data[username] = user_info

        # Освобождаем IP-адрес
        ip_address = user_info.get("address", "").split("/")[0]
        if ip_address in ip_data:
            print(f"🌐 Освобождение IP-адреса {ip_address}...")
            ip_data[ip_address] = False

        # Перемещаем файл конфигурации
        stale_config_path = os.path.join(stale_config_dir, f"{username}.conf")
        if os.path.exists(user_file):
            print(f"📂 Перемещение конфигурационного файла в {stale_config_path}...")
            os.makedirs(stale_config_dir, exist_ok=True)
            os.rename(user_file, stale_config_path)
        else:
            print(f"⚠️ Конфигурационный файл {user_file} отсутствует. Пропускаем шаг перемещения.")

        # Удаляем пользователя из WireGuard
        if os.path.exists(wg_config_path):
            print(f"📂 Чтение конфигурации WireGuard из {wg_config_path}...")
            with open(wg_config_path, "r") as f:
                wg_config = f.read()
            updated_config = "\n".join(
                line
                for line in wg_config.splitlines()
                if username not in line
            )
            print("💾 Сохранение обновлённой конфигурации WireGuard...")
            with open(wg_config_path, "w") as f:
                f.write(updated_config)
            print("🔄 Синхронизация конфигурации WireGuard...")
            subprocess.run(["wg", "syncconf", "wg0", wg_config_path])
        else:
            print(f"⚠️ Конфигурация WireGuard {wg_config_path} не найдена. Пропускаем обновление.")

        # Сохраняем обновлённые данные
        print("💾 Сохранение обновлений...")
        with open(user_records_path, "w") as f:
            json.dump(user_data, f, indent=4)

        with open(stale_records_path, "w") as f:
            json.dump(stale_data, f, indent=4)

        with open(ip_records_path, "w") as f:
            json.dump(ip_data, f, indent=4)

        print(f"✅ Пользователь {username} успешно удалён и перемещён в архив.")
        return f"✅ Пользователь {username} успешно удалён и перемещён в архив."

    except Exception as e:
        print(f"❌ Ошибка при удалении пользователя: {str(e)}")
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
