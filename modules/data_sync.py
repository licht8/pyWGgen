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
                peers[current_peer] = {"peer": current_peer}  # Сохраняем peer
            elif current_peer:
                if "allowed ips:" in line:
                    peers[current_peer]["allowed_ips"] = line.split(":")[1].strip()
                elif "endpoint:" in line:
                    peers[current_peer]["endpoint"] = line.split(":")[1].strip()
                elif "latest handshake:" in line:
                    peers[current_peer]["last_handshake"] = line.split(":")[1].strip()
                elif "transfer:" in line:
                    transfer_data = line.split(":")[1].strip().split(", ")
                    peers[current_peer]["uploaded"] = transfer_data[0]
                    peers[current_peer]["downloaded"] = transfer_data[1]

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
        wg_data = wg_show_data.get(peer_key, {})

        synced_data[username] = {
            "peer": peer_key,
            "username": username,
            "email": details.get("email", "N/A"),
            "telegram_id": details.get("telegram_id", "N/A"),
            "allowed_ips": wg_data.get("allowed_ips", details.get("allowed_ips", "N/A")),
            "endpoint": wg_data.get("endpoint", details.get("endpoint", "N/A")),
            "last_handshake": wg_data.get("last_handshake", details.get("last_handshake", "N/A")),
            "uploaded": wg_data.get("uploaded", details.get("uploaded", "N/A")),
            "downloaded": wg_data.get("downloaded", details.get("downloaded", "N/A")),
            "created": details.get("created", datetime.now().isoformat()),
            "expiry": details.get("expiry", "N/A"),
            "qr_code_path": details.get("qr_code_path", "N/A"),
            "status": "active" if wg_data else "inactive",
        }

    # Проверяем новых пользователей из wg show, которых нет в user_records
    for peer, peer_data in wg_show_data.items():
        if not any(record.get("peer") == peer for record in synced_data.values()):
            print(f"⚠️ Новый пользователь из wg show не найден в базе: {peer_data.get('allowed_ips')}")
            synced_data[f"unknown_{peer}"] = {
                "peer": peer,
                "username": f"unknown_{peer}",
                "email": "N/A",
                "telegram_id": "N/A",
                "allowed_ips": peer_data.get("allowed_ips", "N/A"),
                "endpoint": peer_data.get("endpoint", "N/A"),
                "last_handshake": peer_data.get("last_handshake", "N/A"),
                "uploaded": peer_data.get("uploaded", "N/A"),
                "downloaded": peer_data.get("downloaded", "N/A"),
                "created": datetime.now().isoformat(),
                "expiry": "N/A",
                "qr_code_path": "N/A",
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
