#!/usr/bin/env python3
# modules/sync.py
# Модуль для синхронизации данных WireGuard с проектом

import subprocess
import json
import os

USER_RECORDS_JSON = "user/data/user_records.json"

def load_json(filepath):
    """Загружает JSON файл."""
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            return json.load(file)
    return {}

def save_json(filepath, data):
    """Сохраняет данные в JSON файл."""
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

def parse_wireguard_output(wg_output):
    """Парсит вывод команды `wg show`."""
    lines = wg_output.splitlines()
    users = []
    current_peer = None

    for line in lines:
        if line.startswith("peer:"):
            current_peer = {"peer": line.split()[1]}
        elif current_peer and "allowed ips:" in line:
            current_peer["allowed_ips"] = line.split(":")[1].strip()
            users.append(current_peer)
            current_peer = None

    return users

def sync_users_with_wireguard():
    """Синхронизирует пользователей WireGuard с JSON-файлами."""
    try:
        wg_output = subprocess.check_output(["wg", "show"], text=True)
        wg_users = parse_wireguard_output(wg_output)
        existing_users = load_json(USER_RECORDS_JSON)

        updated = False
        for user in wg_users:
            peer = user.get("peer")
            if peer and peer not in existing_users:
                existing_users[peer] = {
                    "peer": user["peer"],
                    "allowed_ips": user["allowed_ips"],
                    "status": "active"
                }
                updated = True

        if updated:
            save_json(USER_RECORDS_JSON, existing_users)
            print("✅ Пользователи синхронизированы с WireGuard.")
        else:
            print("🔄 Пользователи уже синхронизированы.")
    except Exception as e:
        print(f"❌ Ошибка синхронизации пользователей: {e}")
