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
    """Синхронизирует пользователей WireGuard с JSON-файлами проекта."""
    try:
        # Читаем вывод команды wg show
        wg_output = subprocess.check_output(["wg", "show"], text=True)
        wg_users = parse_wireguard_output(wg_output)

        if not wg_users:
            print("⚠️ Нет пользователей в выводе WireGuard.")
            return

        # Загружаем записи пользователей
        user_records = load_json(USER_RECORDS_JSON)

        # Создаем сопоставление публичных ключей и имен пользователей
        key_to_username = {
            record["public_key"]: username
            for username, record in user_records.items()
            if "public_key" in record
        }

        # Обновляем пользователей
        synced_users = {}
        for peer, data in wg_users.items():
            username = key_to_username.get(peer, peer)  # Если имя не найдено, используем ключ
            synced_users[username] = {
                "public_key": peer,
                **data,
                "status": "active" if data.get("last_handshake") else "inactive"
            }

        # Сохраняем данные в wg_users.json
        save_json(WG_USERS_JSON, synced_users)
        print("✅ Пользователи успешно синхронизированы.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка выполнения команды WireGuard: {e}")
    except Exception as e:
        print(f"❌ Ошибка синхронизации пользователей: {e}")

if __name__ == "__main__":
    sync_users_with_wireguard()
