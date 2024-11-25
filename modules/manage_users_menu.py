#!/usr/bin/env python3
# modules/manage_users_menu.py
# Меню управления пользователями WireGuard

import json
import os

USER_RECORDS_FILE = "user/data/user_records.json"

def load_user_records():
    """Загрузка данных пользователей."""
    if os.path.exists(USER_RECORDS_FILE):
        with open(USER_RECORDS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_records(user_records):
    """Сохранение данных пользователей."""
    with open(USER_RECORDS_FILE, "w") as f:
        json.dump(user_records, f, indent=4)

def create_user():
    """Создание нового пользователя."""
    username = input("Введите имя пользователя: ").strip()
    telegram_id = input("Введите Telegram ID (или оставьте пустым): ").strip()
    allowed_ips = input("Введите разрешенные IP-адреса (например, 10.66.66.5): ").strip()

    user_records = load_user_records()
    if username in user_records:
        print("❌ Пользователь с таким именем уже существует.")
        return

    user_records[username] = {
        "username": username,
        "telegram_id": telegram_id or "N/A",
        "allowed_ips": allowed_ips,
        "status": "inactive",
    }
    save_user_records(user_records)
    print(f"✅ Пользователь {username} успешно создан.")

def manage_users_menu():
    """Меню управления пользователями."""
    while True:
        print("\n========== Управление пользователями ==========")
        print("1. 🌱 Создать пользователя")
        print("2. 🔍 Показать всех пользователей")
        print("0. Вернуться в главное меню")
        print("===============================================")

        choice = input("Выберите действие: ").strip()
        if choice == "1":
            create_user()
        elif choice == "2":
            user_records = load_user_records()
            if not user_records:
                print("⚠️ Список пользователей пуст.")
            else:
                for username, data in user_records.items():
                    print(f"👤 {username} | Telegram: {data.get('telegram_id', 'N/A')} | Peer: {data.get('peer', 'N/A')}")
        elif choice == "0":
            break
        else:
            print("⚠️ Некорректный выбор. Попробуйте снова.")
