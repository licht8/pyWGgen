#!/usr/bin/env python3
# delete_user.py
## Скрипт для удаления пользователей из WireGuard и связанных записей.

import os
import json
import subprocess
from datetime import datetime
from modules.utils import read_json, write_json, get_wireguard_config_path

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
    wg_config_path = get_wireguard_config_path()

    if not os.path.exists(user_records_path):
        return "❌ Файл user_records.json не найден."

    try:
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

        # Обновление записей пользователей
        write_json(user_records_path, user_data)

        # Удаление пользователя из конфигурации WireGuard
        if os.path.exists(wg_config_path):
            with open(wg_config_path, "r") as f:
                config_lines = f.readlines()

            updated_lines = []
            inside_peer_block = False

            for line in config_lines:
                # Определяем начало блока [Peer]
                if line.strip() == "[Peer]":
                    inside_peer_block = True
                    current_block = []

                # Если мы внутри блока [Peer], собираем строки
                if inside_peer_block:
                    current_block.append(line)
                    # Если строка содержит имя пользователя, блок удаляется
                    if f"### Client {username}" in line:
                        inside_peer_block = False  # Завершаем блок и не добавляем его в updated_lines
                    continue  # Пропускаем обработку строк текущего блока

                # Если блок закончился и не содержит имени пользователя, добавляем его в результат
                if not inside_peer_block and current_block:
                    updated_lines.extend(current_block)
                    current_block = []

                # Добавляем строки, не входящие в блок [Peer]
                if not inside_peer_block:
                    updated_lines.append(line)

            # Обновляем конфигурацию WireGuard
            with open(wg_config_path, "w") as f:
                f.writelines(updated_lines)

            # Синхронизация конфигурации
            subprocess.run(["wg", "syncconf", "wg0", wg_config_path], check=True)

        return f"✅ Пользователь {username} успешно удалён."
    except Exception as e:
        return f"❌ Ошибка при удалении пользователя {username}: {str(e)}"

