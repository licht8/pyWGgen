#!/usr/bin/env python3
# delete_user.py
## Скрипт для удаления пользователей из WireGuard и связанных записей.

import os
import json
import subprocess
from datetime import datetime
from modules.utils import read_json, write_json, get_wireguard_config_path, log_debug

def delete_user(username):
    """
    Удаление пользователя из конфигурации WireGuard и связанных файлов.
    :param username: Имя пользователя для удаления.
    :return: Сообщение об успехе или ошибке.
    """
    # Пути к файлам и директориям
    base_dir = os.getcwd()
    user_records_path = os.path.join(base_dir, "user", "data", "user_records.json")
    ip_records_path = os.path.join(base_dir, "user", "data", "ip_records.json")
    stale_records_path = os.path.join(base_dir, "user", "stale_user_records.json")
    stale_config_dir = os.path.join(base_dir, "user", "stale_config")
    user_file = os.path.join(base_dir, "user", "data", f"{username}.conf")
    
    if not os.path.exists(user_records_path):
        return "❌ Файл user_records.json не найден."

    try:
        log_debug(f"Начало удаления пользователя: {username}")
        
        # Чтение записей пользователей
        user_data = read_json(user_records_path)
        if username not in user_data:
            return f"❌ Пользователь {username} не найден."
        
        # Удаление записи пользователя
        user_info = user_data.pop(username)
        user_info["removed_at"] = datetime.now().isoformat()

        # Чтение и обновление записей IP-адресов
        if os.path.exists(ip_records_path):
            ip_data = read_json(ip_records_path)
            ip_address = user_info.get("address", "").split("/")[0]
            if ip_address in ip_data:
                ip_data[ip_address] = False
            write_json(ip_records_path, ip_data)

        # Перемещение конфигурации пользователя в архив
        if os.path.exists(user_file):
            stale_file = os.path.join(stale_config_dir, f"{username}.conf")
            os.makedirs(stale_config_dir, exist_ok=True)
            os.rename(user_file, stale_file)

        # Сохранение устаревших записей
        stale_data = read_json(stale_records_path)
        stale_data[username] = user_info
        write_json(stale_records_path, stale_data)

        # Удаление пользователя из WireGuard
        public_key = extract_public_key(user_file)
        if public_key:
            subprocess.run(["sudo", "wg", "set", "wg0", "peer", public_key, "remove"], check=True)
            log_debug(f"Пользователь {username} с ключом {public_key} удален из WireGuard.")

        # Обновление записей пользователей
        write_json(user_records_path, user_data)

        return f"✅ Пользователь {username} успешно удалён."
    except subprocess.CalledProcessError as e:
        log_debug(f"Ошибка при удалении пользователя {username}: {e.stderr.strip() if e.stderr else 'Unknown error'}")
        return f"❌ Ошибка при удалении пользователя {username}: {e.stderr.strip() if e.stderr else 'Unknown error'}"
    except Exception as e:
        log_debug(f"Ошибка при удалении пользователя {username}: {str(e)}")
        return f"❌ Ошибка при удалении пользователя {username}: {str(e)}"


def extract_public_key(user_file):
    """
    Извлечение публичного ключа из конфигурации пользователя.
    :param user_file: Путь к файлу конфигурации пользователя.
    :return: Публичный ключ или None.
    """
    if not os.path.exists(user_file):
        return None
    with open(user_file, "r") as f:
        for line in f:
            if line.strip().startswith("PublicKey"):
                return line.split("=", 1)[1].strip()
    return None
