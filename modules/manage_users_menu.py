#!/usr/bin/env python3
# modules/manage_users_menu.py
# Модуль для управления пользователями WireGuard

import os
import json
import subprocess
from modules.utils import get_wireguard_subnet, read_json, write_json
import sys
from settings import USER_DB_PATH, SERVER_CONFIG_FILE, WG_CONFIG_DIR, QR_CODE_DIR

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
            ["python3", os.path.join("main.py"), username, email, telegram_id],
            check=True,
            cwd=os.path.abspath(os.path.dirname(__file__) + "/../")
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


def delete_user():
    """
    Удаление пользователя из конфигурации WireGuard и связанных файлов.
    """
    username = input("Введите имя пользователя для удаления: ").strip()
    if not username:
        print("❌ Ошибка: имя пользователя не может быть пустым.")
        return

    print(f"➡️ Начинаем удаление пользователя: '{username}'.")

    if not os.path.exists(USER_DB_PATH):
        print(f"❌ Файл данных пользователей не найден: {USER_DB_PATH}")
        return

    try:
        # Чтение данных пользователей
        user_data = read_json(USER_DB_PATH)
        if username not in user_data:
            print(f"❌ Пользователь '{username}' не существует.")
            return

        # Удаление записи пользователя
        user_data.pop(username)
        write_json(USER_DB_PATH, user_data)
        print(f"📝 Запись пользователя '{username}' удалена из данных.")

        # Удаление конфигурации пользователя
        wg_config_path = WG_CONFIG_DIR / f"{username}.conf"
        if wg_config_path.exists():
            wg_config_path.unlink()
            print(f"🗑️ Конфигурация '{wg_config_path}' удалена.")

        # Удаление QR-кода пользователя
        qr_code_path = QR_CODE_DIR / f"{username}.png"
        if qr_code_path.exists():
            qr_code_path.unlink()
            print(f"🗑️ QR-код '{qr_code_path}' удалён.")

        # Извлечение публичного ключа пользователя
        public_key = extract_public_key(username, SERVER_CONFIG_FILE)
        if not public_key:
            print(f"❌ Публичный ключ пользователя '{username}' не найден в конфигурации WireGuard.")
            return

        # Удаление пользователя из WireGuard
        subprocess.run(["sudo", "wg", "set", "wg0", "peer", public_key, "remove"], check=True)
        print(f"🔐 Пользователь '{username}' удален из WireGuard.")

        # Обновление конфигурации WireGuard
        remove_peer_from_config(public_key, SERVER_CONFIG_FILE, username)
        print(f"✅ Конфигурация WireGuard успешно обновлена.")

        print(f"✅ Пользователь '{username}' успешно удалён.")
    except Exception as e:
        print(f"⚠️ Ошибка при удалении пользователя '{username}': {e}")

def extract_public_key(username, config_path):
    """
    Извлечение публичного ключа пользователя из конфигурации WireGuard.
    :param username: Имя пользователя.
    :param config_path: Путь к конфигурационному файлу WireGuard.
    :return: Публичный ключ пользователя.
    """
    try:
        with open(config_path, "r") as f:
            lines = f.readlines()

        found_username = False
        for line in lines:
            if username in line:
                found_username = True
            elif found_username and line.strip().startswith("PublicKey"):
                return line.split("=", 1)[1].strip()
        return None
    except Exception as e:
        print(f"⚠️ Ошибка при поиске публичного ключа: {e}")
        return None

def remove_peer_from_config(public_key, config_path, client_name):
    """
    Удаление записи [Peer] и связанного комментария из конфигурационного файла WireGuard.
    :param public_key: Публичный ключ пользователя.
    :param config_path: Путь к конфигурационному файлу WireGuard.
    :param client_name: Имя клиента.
    """
    try:
        with open(config_path, "r") as f:
            lines = f.readlines()

        updated_lines = []
        skip_lines = 0

        for line in lines:
            # Если найден комментарий клиента
            if line.strip() == f"### Client {client_name}":
                skip_lines = 5  # Удаляем 5 строк начиная с этого момента
                continue

            # Пропуск строк, связанных с удаляемым блоком
            if skip_lines > 0:
                skip_lines -= 1
                continue

            # Сохранение остальных строк
            updated_lines.append(line)

        # Запись обновленной конфигурации
        with open(config_path, "w") as f:
            f.writelines(updated_lines)
    except Exception as e:
        print(f"⚠️ Ошибка при обновлении конфигурации: {e}")

def manage_users_menu():
    """Меню управления пользователями."""
    while True:
        print("\n========== Управление пользователями ==========")
        print("1. 🌱 Создать пользователя")
        print("2. 🔍 Показать всех пользователей")
        print("3. ❌ Удалить пользователя")
        print("0. Вернуться в главное меню")
        print("===============================================")

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
