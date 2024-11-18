import os
import json
import subprocess
from datetime import datetime

def delete_user(username):
    """Удаление пользователя."""
    base_dir = os.getcwd()
    user_records_path = os.path.join(base_dir, "user", "data", "user_records.json")
    ip_records_path = os.path.join(base_dir, "user", "data", "ip_records.json")
    wg_config_path = os.path.join(base_dir, "user", "data", "wg_configs/wg0.conf")
    stale_records_path = os.path.join(base_dir, "user", "stale_user_records.json")
    stale_config_dir = os.path.join(base_dir, "user", "stale_config")
    user_file = os.path.join(base_dir, "user", "data", f"{username}.conf")

    if not os.path.exists(user_records_path):
        return "❌ Файл user_records.json не найден."

    try:
        with open(user_records_path, "r") as f:
            user_data = json.load(f)

        if username not in user_data:
            return f"❌ Пользователь {username} не найден."

        user_info = user_data.pop(username)
        user_info["removed_at"] = datetime.now().isoformat()

        if os.path.exists(ip_records_path):
            with open(ip_records_path, "r") as f:
                ip_data = json.load(f)
            ip_address = user_info.get("address", "").split("/")[0]
            if ip_address in ip_data:
                ip_data[ip_address] = False
            with open(ip_records_path, "w") as f:
                json.dump(ip_data, f, indent=4)

        if os.path.exists(user_file):
            stale_file = os.path.join(stale_config_dir, f"{username}.conf")
            os.makedirs(stale_config_dir, exist_ok=True)
            os.rename(user_file, stale_file)

        with open(stale_records_path, "w") as f:
            json.dump({username: user_info}, f, indent=4)

        with open(user_records_path, "w") as f:
            json.dump(user_data, f, indent=4)

        if os.path.exists(wg_config_path):
            with open(wg_config_path, "r") as f:
                config_lines = f.readlines()
            updated_lines = [line for line in config_lines if username not in line]
            with open(wg_config_path, "w") as f:
                f.writelines(updated_lines)
            subprocess.run(["wg", "syncconf", "wg0", wg_config_path])

        return f"✅ Пользователь {username} успешно удалён."
    except Exception as e:
        return f"❌ Ошибка при удалении пользователя {username}: {str(e)}"
