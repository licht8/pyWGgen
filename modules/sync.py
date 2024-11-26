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

def sync_wireguard_config(interface="wg0"):
    """
    Обновляет конфигурацию WireGuard.
    """
    try:
        subprocess.run(["wg-quick", "save", interface], check=True)
        print(f"✅ Конфигурация WireGuard {interface} успешно сохранена.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при сохранении конфигурации WireGuard: {e}")

def sync_users_with_wireguard():
    """Синхронизирует пользователей WireGuard с JSON-файлами проекта."""
    try:
        print("🔄 Получение информации из WireGuard...")
        wg_output = subprocess.check_output(["wg", "show"], text=True)
        wg_users = parse_wireguard_output(wg_output)

        if not wg_users:
            print("⚠️ Нет пользователей в выводе WireGuard.")
            return

        # Загружаем существующие записи
        existing_users = load_json(USER_RECORDS_JSON)

        updated = False
        for user in wg_users:
            peer = user.get("peer")
            if peer:
                if peer not in existing_users:
                    print(f"➕ Добавление нового пользователя: {peer}")
                    existing_users[peer] = {
                        "peer": user["peer"],
                        "allowed_ips": user["allowed_ips"],
                        "status": "active"
                    }
                    updated = True
                elif existing_users[peer].get("allowed_ips") != user["allowed_ips"]:
                    print(f"✏️ Обновление IP пользователя {peer}: {user['allowed_ips']}")
                    existing_users[peer]["allowed_ips"] = user["allowed_ips"]
                    updated = True

        # Сохранение обновленных данных
        if updated:
            save_json(USER_RECORDS_JSON, existing_users)
            print("✅ Пользователи синхронизированы с WireGuard.")
        else:
            print("🔄 Все пользователи уже актуальны.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка выполнения команды WireGuard: {e}")
    except Exception as e:
        print(f"❌ Ошибка синхронизации пользователей: {e}")

if __name__ == "__main__":
    sync_users_with_wireguard()
