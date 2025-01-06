#!/usr/bin/env python3
# modules/manage_users_menu.py
# Модуль для управления пользователями WireGuard

import os
import json
import subprocess
from modules.utils import get_wireguard_subnet, read_json, write_json
import sys
import settings
from settings import USER_DB_PATH

def ensure_directory_exists(filepath):
    """Убедитесь, что директория для файла существует."""
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_user_records():
    """Загрузка данных пользователей из JSON."""
    return read_json(USER_DB_PATH)

def create_user():
    """Создание нового пользователя через вызов main.py."""
    username = input("Введите имя пользователя: ").strip()
    if not username:
        print("❌ Имя пользователя не может быть пустым.")
        return

    email = input("Введите email (необязательно): ").strip() or "N/A"
    telegram_id = input("Введите Telegram ID (необязательно): ").strip() or "N/A"

    try:
        subprocess.run(
            ["python3", os.path.join("wg_qr_generator", "main.py"), username, email, telegram_id],
            check=True,
            cwd=os.path.abspath(os.path.dirname(__file__) + "/../../")
        )

    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при создании пользователя: {e}")


def list_users():
    """Вывод списка всех пользователей."""
    records = load_user_records()
    if not records:
        print("⚠️ Список пользователей пуст.")
        return

    print("\n👤 Пользователи WireGuard:")
    for username, data in records.items():
        allowed_ips = data.get("allowed_ips", "N/A")
        status = data.get("status", "N/A")
        print(f"  - {username}: {allowed_ips} | Статус: {status}")


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
            list_users()
        elif choice in {"0", "q"}:
            break
        else:
            print("⚠️ Некорректный выбор. Попробуйте снова.")
