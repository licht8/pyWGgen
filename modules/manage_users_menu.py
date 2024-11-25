#!/usr/bin/env python3
# modules/manage_users_menu.py
# Меню управления пользователями WireGuard

import os
import json

USER_RECORDS_FILE = "user/data/user_records.json"

def load_user_records():
    """Загружает записи пользователей."""
    if os.path.exists(USER_RECORDS_FILE):
        with open(USER_RECORDS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_user_records(records):
    """Сохраняет записи пользователей."""
    with open(USER_RECORDS_FILE, "w") as file:
        json.dump(records, file, indent=4)

def create_user():
    """Создаёт нового пользователя."""
    username = input("Введите имя пользователя: ").strip()
    allowed_ips = input("Введите разрешённые IP (например, 10.66.66.5): ").strip()

    records = load_user_records()
    if username in records:
        print("❌ Пользователь с таким именем уже существует.")
        return

    records[username] = {
        "allowed_ips": allowed_ips,
        "status": "active"
    }
    save_user_records(records)
    print(f"✅ Пользователь {username} успешно создан.")

def delete_user():
    """Удаляет пользователя."""
    username = input("Введите имя пользователя для удаления: ").strip()
    records = load_user_records()

    if username not in records:
        print("❌ Пользователь не найден.")
        return

    del records[username]
    save_user_records(records)
    print(f"✅ Пользователь {username} успешно удалён.")

def list_users():
    """Показывает всех пользователей."""
    records = load_user_records()
    if not records:
        print("⚠️ Список пользователей пуст.")
    else:
        print("\nСписок пользователей:")
        for username, details in records.items():
            print(f"👤 {username}: {details}")

def manage_users_menu():
    """Меню управления пользователями."""
    while True:
        print("\n==========  Управление пользователями  ==========")
        print(" 1. 🌱  Создать пользователя")
        print(" 2. 🔍  Показать всех пользователей")
        print(" 3. 🗑️  Удалить пользователя")
        print(" 0. 👈  Вернуться в главное меню")
        print(" ================================================")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            create_user()
        elif choice == "2":
            list_users()
        elif choice == "3":
            delete_user()
        elif choice in {"0", "q"}:
            break
        else:
            print("⚠️ Некорректный выбор. Попробуйте снова.")
