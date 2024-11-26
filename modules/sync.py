#!/usr/bin/env python3
# modules/sync.py
# Модуль для синхронизации данных WireGuard с проектом

#!/usr/bin/env python3
# modules/sync.py
import subprocess
import json
import os

USER_RECORDS_JSON = "user/data/user_records.json"
WG_USERS_JSON = "logs/wg_users.json"

def load_json(filepath):
    """Загружает JSON файл."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"⚠️ Файл {filepath} поврежден. Создаем новый.")
            return {}
    return {}

def save_json(filepath, data):
    """Сохраняет данные в JSON файл."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

def parse_wireguard_output(wg_output):
    """Парсит вывод команды `wg show`."""
    lines = wg_output.splitlines()
    peers = {}
    current_peer = None

    for line in lines:
        if line.startswith("peer:"):
            current_peer = line.split()[1]
            peers[current_peer] = {}
        elif current_peer:
            if "allowed ips:" in line:
                peers[current_peer]["allowed_ips"] = line.split(":")[1].strip()
            elif "latest handshake:" in line:
                peers[current_peer]["last_handshake"] = line.split(":")[1].strip()
            elif "transfer:" in line:
                transfer = line.split(":")[1].strip().split(", ")
                peers[current_peer]["uploaded"] = transfer[0].replace("received ", "")
                peers[current_peer]["downloaded"] = transfer[1].replace("sent ", "")
    return peers

def sync_users_with_wireguard():
    """Синхронизирует пользователей WireGuard с JSON-файлами."""
    try:
        wg_output = subprocess.check_output(["wg", "show"], text=True)
        wg_users = parse_wireguard_output(wg_output)
        if not wg_users:
            print("⚠️ Нет пользователей в выводе WireGuard.")
            return

        existing_users = load_json(WG_USERS_JSON)
        updated_users = {**existing_users, **wg_users}
        save_json(WG_USERS_JSON, updated_users)
        print("✅ Пользователи успешно синхронизированы.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка выполнения команды WireGuard: {e}")
    except Exception as e:
        print(f"❌ Ошибка синхронизации пользователей: {e}")

if __name__ == "__main__":
    sync_users_with_wireguard()
