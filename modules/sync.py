#!/usr/bin/env python3
# modules/sync.py
# Модуль для синхронизации пользователей WireGuard с проектом

import json
from pathlib import Path
from settings import USER_DB_PATH, SERVER_CONFIG_FILE
from modules.main_registration_fields import create_user_record

def sync_users_from_config():
    """
    Синхронизирует пользователей из конфигурационного файла WireGuard с user_records.json.
    """
    try:
        # Чтение конфигурационного файла WireGuard
        with open(SERVER_CONFIG_FILE, "r") as f:
            config_lines = f.readlines()

        # Парсинг пользователей из конфигурации
        users_in_config = []
        current_user = {}

        for line in config_lines:
            stripped_line = line.strip()

            # Ищем комментарий ### Client <name>
            if stripped_line.startswith("### Client"):
                if current_user:
                    users_in_config.append(current_user)  # Сохраняем предыдущего пользователя
                current_user = {"username": stripped_line.split("### Client")[1].strip()}
            
            # Извлекаем PublicKey, PresharedKey и AllowedIPs
            elif stripped_line.startswith("PublicKey ="):
                current_user["public_key"] = stripped_line.split("PublicKey =")[1].strip()
            elif stripped_line.startswith("PresharedKey ="):
                current_user["preshared_key"] = stripped_line.split("PresharedKey =")[1].strip()
            elif stripped_line.startswith("AllowedIPs ="):
                current_user["allowed_ips"] = stripped_line.split("AllowedIPs =")[1].strip()
            
            # Конец блока [Peer]
            elif stripped_line == "" and current_user:
                users_in_config.append(current_user)
                current_user = {}

        # Добавляем последнего пользователя, если он есть
        if current_user:
            users_in_config.append(current_user)

        print(f"[DEBUG] Users in config: {users_in_config}")

        # Чтение текущих записей в user_records.json
        user_records = {}
        if Path(USER_DB_PATH).exists():
            with open(USER_DB_PATH, "r") as f:
                user_records = json.load(f)

        # Синхронизация пользователей
        new_users = 0
        for user in users_in_config:
            username = user["username"]
            if username not in user_records:
                # Создание нового пользователя с использованием create_user_record
                user_record = create_user_record(
                    username=username,
                    address=user["allowed_ips"],
                    public_key=user["public_key"],
                    preshared_key=user["preshared_key"],
                    qr_code_path=f"user/data/qrcodes/{username}.png"  # Путь к QR-коду
                )
                user_records[username] = user_record
                new_users += 1

        # Сохраняем обновлённый user_records.json
        with open(USER_DB_PATH, "w") as f:
            json.dump(user_records, f, indent=4)

        print(f"[INFO] Sync complete. {new_users} new user(s) added.")
        return f"Sync complete. {new_users} new user(s) added."

    except Exception as e:
        print(f"[ERROR] Failed to sync users: {e}")
        return f"Failed to sync users: {e}"