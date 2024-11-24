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
    """Синхронизирует данные из всех источников."""
    user_records = load_json(USER_RECORDS_JSON)
    wg_show_data = get_wg_show_data()

    synced_data = {}

    for username, details in user_records.items():
        peer_key = details.get("peer", "N/A")
        wg_data = next(
            (wg for wg, wg_details in wg_show_data.items() if wg_details.get("allowed_ips") == details.get("allowed_ips")),
            peer_key
        )

        # Обновляем или оставляем существующие поля
        synced_data[username] = {
            "peer": wg_data,
            "username": username,
            "email": details.get("email", "N/A"),
            "telegram_id": details.get("telegram_id", "N/A"),
            "allowed_ips": wg_show_data.get(wg_data, {}).get("allowed_ips", details.get("allowed_ips", "N/A")),
            "endpoint": wg_show_data.get(wg_data, {}).get("endpoint", details.get("endpoint", "N/A")),
            "last_handshake": wg_show_data.get(wg_data, {}).get("latest_handshake", details.get("last_handshake", "N/A")),
            "uploaded": wg_show_data.get(wg_data, {}).get("sent", details.get("uploaded", "N/A")),
            "downloaded": wg_show_data.get(wg_data, {}).get("received", details.get("downloaded", "N/A")),
            "created": details.get("created_at", "N/A"),
            "expiry": details.get("expires_at", "N/A"),
            "qr_code_path": details.get("qr_code_path", "N/A"),
            "status": "active" if wg_data else "inactive",
        }

    # Сохранение данных
    with open(USER_RECORDS_JSON, "w") as user_records_file:
        json.dump(synced_data, user_records_file, indent=4)
    with open(WG_USERS_JSON, "w") as wg_users_file:
        json.dump(synced_data, wg_users_file, indent=4)

    print(f"✅ Данные успешно синхронизированы. Файлы обновлены:\n - {WG_USERS_JSON}\n - {USER_RECORDS_JSON}")
    return synced_data


if __name__ == "__main__":
    sync_user_data()
