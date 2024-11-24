#!/usr/bin/env python3
# modules/data_sync.py
# Утилита для синхронизации данных о пользователях WireGuard

import os
import json
import subprocess
from datetime import datetime

# Пути к данным
WG_USERS_JSON = os.path.join("logs", "wg_users.json")
USER_RECORDS_JSON = os.path.join("user", "data", "user_records.json")


def load_json(filepath):
    """Загружает данные из JSON-файла."""
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_json(filepath, data):
    """Сохраняет данные в JSON-файл."""
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)


def get_wg_show_data():
    """Получает данные команды 'wg show'."""
    try:
        output = subprocess.check_output(["wg", "show"], text=True)
        peers = {}
        current_peer = None

        for line in output.splitlines():
            if line.startswith("peer:"):
                current_peer = line.split(":")[1].strip()
                peers[current_peer] = {}
            elif current_peer:
                if "allowed ips:" in line:
                    peers[current_peer]["allowed_ips"] = line.split(":")[1].strip()
                elif "endpoint:" in line:
                    peers[current_peer]["endpoint"] = line.split(":")[1].strip()
                elif "latest handshake:" in line:
                    peers[current_peer]["latest_handshake"] = line.split(":")[1].strip()
                elif "transfer:" in line:
                    transfer_data = line.split(":")[1].strip().split(", ")
                    peers[current_peer]["received"] = transfer_data[0]
                    peers[current_peer]["sent"] = transfer_data[1]

        return peers
    except subprocess.CalledProcessError:
        return {}


def sync_user_data():
    """Синхронизирует данные пользователей."""
    user_records = load_json(USER_RECORDS_JSON)
    wg_show_data = get_wg_show_data()

    synced_data = {}
    updated_user_records = user_records.copy()

    for username, details in user_records.items():
        peer_key = details.get("peer")
        wg_data = wg_show_data.get(peer_key, {})

        synced_data[username] = {
            "username": username,
            "allowed_ips": wg_data.get("allowed_ips", "N/A"),
            "endpoint": wg_data.get("endpoint", "N/A"),
            "last_handshake": wg_data.get("latest_handshake", "N/A"),
            "uploaded": wg_data.get("sent", "N/A"),
            "downloaded": wg_data.get("received", "N/A"),
            "created": details.get("created_at", "N/A"),
            "expiry": details.get("expires_at", "N/A"),
            "status": "active" if "latest_handshake" in wg_data and wg_data["latest_handshake"] != "N/A" else "inactive",
        }

    # Дополнение user_records новыми данными
    for peer, wg_data in wg_show_data.items():
        if not any(details.get("peer") == peer for details in user_records.values()):
            new_user = {
                "peer": peer,
                "created_at": datetime.now().isoformat(),
                "expires_at": "N/A",
                "address": wg_data.get("allowed_ips", "N/A"),
            }
            username = f"user_{peer[:6]}"  # Создаём временное имя пользователя
            updated_user_records[username] = new_user

    # Сохраняем обновленные данные
    save_json(WG_USERS_JSON, synced_data)
    save_json(USER_RECORDS_JSON, updated_user_records)

    print(f"✅ Данные успешно синхронизированы. Файлы обновлены:")
    print(f" - {WG_USERS_JSON}")
    print(f" - {USER_RECORDS_JSON}")
    return synced_data


if __name__ == "__main__":
    sync_user_data()
