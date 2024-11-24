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

    # Обработка пользователей из user_records.json
    for username, details in user_records.items():
        user_address = details.get("allowed_ips", "N/A")
        matched_peer = None

        # Сопоставление по адресу из user_records.json
        for peer, peer_data in wg_show_data.items():
            if user_address == peer_data.get("allowed_ips"):
                matched_peer = peer
                break

        wg_data = wg_show_data.get(matched_peer, {})

        # Обновляем данные для существующего пользователя
        synced_data[username] = {
            "username": username,
            "allowed_ips": user_address,
            "endpoint": wg_data.get("endpoint", "N/A"),
            "last_handshake": wg_data.get("latest_handshake", "N/A"),
            "uploaded": wg_data.get("sent", "N/A"),
            "downloaded": wg_data.get("received", "N/A"),
            "created": details.get("created_at", "N/A"),
            "expiry": details.get("expires_at", "N/A"),
            "status": "active" if matched_peer else "inactive",
        }

    # Добавление новых пользователей только если они отсутствуют в user_records.json
    for peer, peer_data in wg_show_data.items():
        # Проверяем, нет ли такого адреса в synced_data
        if not any(record.get("allowed_ips") == peer_data.get("allowed_ips") for record in synced_data.values()):
            print(f"⚠️ Новый пользователь из wg show не найден в базе: {peer_data.get('allowed_ips')}")
            username = f"user_{peer[:6]}"
            synced_data[username] = {
                "username": username,
                "allowed_ips": peer_data.get("allowed_ips", "N/A"),
                "endpoint": peer_data.get("endpoint", "N/A"),
                "last_handshake": peer_data.get("latest_handshake", "N/A"),
                "uploaded": peer_data.get("sent", "N/A"),
                "downloaded": peer_data.get("received", "N/A"),
                "created": datetime.now().isoformat(),
                "expiry": "N/A",
                "status": "active",
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
