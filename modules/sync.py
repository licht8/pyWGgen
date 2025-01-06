#!/usr/bin/env python3
# modules/sync.py
# Модуль для синхронизации пользователей WireGuard с проектом

import subprocess
import json
import os
from settings import USER_DB_PATH

WG_USERS_JSON = "logs/wg_users.json"

def load_json(filepath):
    """Загружает JSON-файл."""
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print(f"⚠️ Файл {filepath} поврежден. Создаем новый.")
                return {}
    return {}

def save_json(filepath, data):
    """Сохраняет данные в JSON-файл."""
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
            current_peer = line.split(":")[1].strip()
            peers[current_peer] = {"last_handshake": "N/A", "allowed_ips": "N/A"}
        elif current_peer and line.strip().startswith("allowed ips:"):
            peers[current_peer]["allowed_ips"] = line.split(":")[1].strip()
        elif current_peer and line.strip().startswith("latest handshake:"):
            peers[current_peer]["last_handshake"] = line.split(":")[1].strip()

    return peers

def sync_users_with_wireguard():
    """Синхронизирует пользователей WireGuard с JSON-файлами."""
    try:
        print("🔄 Получение информации из WireGuard...")
        wg_output = subprocess.check_output(["wg", "show"], text=True)
        wg_users = parse_wireguard_output(wg_output)

        user_records = load_json(USER_DB_PATH)
        users_json = load_json(WG_USERS_JSON)

        key_to_username = {
            record.get("public_key", ""): username
            for username, record in user_records.items()
        }

        for public_key, data in wg_users.items():
            username = key_to_username.get(public_key, "unknown_user")
            users_json[username] = {
                "public_key": public_key,
                **data,
                "status": "active" if data["last_handshake"] != "N/A" else "inactive"
            }

        save_json(WG_USERS_JSON, users_json)
        print("✅ Пользователи успешно синхронизированы.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка выполнения команды WireGuard: {e}")
    except Exception as e:
        print(f"❌ Ошибка синхронизации пользователей: {e}")

if __name__ == "__main__":
    sync_users_with_wireguard()
