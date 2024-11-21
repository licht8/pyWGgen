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
    wg_config_path = get_wireguard_config_path()

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

        # Обновление записей пользователей
        write_json(user_records_path, user_data)

        # Удаление пользователя из конфигурации WireGuard
        if os.path.exists(wg_config_path):
            with open(wg_config_path, "r") as f:
                config_lines = f.readlines()

            updated_lines = [line for line in config_lines if username not in line]
            with open(wg_config_path, "w") as f:
                f.writelines(updated_lines)

            log_debug(f"Конфигурация WireGuard обновлена: {wg_config_path}")
            format_wireguard_config(wg_config_path)

            log_debug(f"Проверяем конфигурацию WireGuard: {wg_config_path}")
            validate_wireguard_config(wg_config_path)

            subprocess.run(["wg", "syncconf", "wg0", wg_config_path], check=True)

        return f"✅ Пользователь {username} успешно удалён."
    except subprocess.CalledProcessError as e:
        log_debug(f"Ошибка при синхронизации WireGuard: {e.stderr.strip() if e.stderr else 'Unknown error'}")
        return f"❌ Ошибка при удалении пользователя {username}: Ошибка при синхронизации WireGuard: {e.stderr.strip() if e.stderr else 'Unknown error'}"
    except Exception as e:
        log_debug(f"Ошибка при удалении пользователя {username}: {str(e)}")
        return f"❌ Ошибка при удалении пользователя {username}: {str(e)}"


def format_wireguard_config(config_path):
    """
    Приведение конфигурации WireGuard к корректному формату.
    Удаляет лишние записи и дублирующиеся блоки.
    """
    log_debug(f"Форматируем файл конфигурации: {config_path}")
    with open(config_path, "r") as f:
        lines = f.readlines()

    formatted_lines = []
    seen_peers = set()
    current_peer = []
    addresses = []

    for line in lines:
        # Сбор всех строк Address
        if line.strip().startswith("Address ="):
            address = line.split("=", 1)[1].strip()
            addresses.append(address)
            continue

        # Обработка блоков [Peer]
        if line.strip() == "[Peer]":
            if current_peer:
                peer_key = "".join(current_peer)
                if peer_key not in seen_peers:
                    formatted_lines.extend(current_peer)
                    seen_peers.add(peer_key)
            current_peer = [line]
        elif current_peer:
            current_peer.append(line)
            if line.strip() == "":
                peer_key = "".join(current_peer)
                if peer_key not in seen_peers:
                    formatted_lines.extend(current_peer)
                    seen_peers.add(peer_key)
                current_peer = []
        else:
            formatted_lines.append(line)

    # Добавление последнего блока [Peer], если он уникален
    if current_peer:
        peer_key = "".join(current_peer)
        if peer_key not in seen_peers:
            formatted_lines.extend(current_peer)

    # Форматирование строки Address
    if addresses:
        formatted_lines.insert(1, f"Address = {', '.join(addresses)}\n")

    with open(config_path, "w") as f:
        f.writelines(formatted_lines)
    log_debug("Форматирование файла завершено.")


def validate_wireguard_config(config_path):
    """
    Проверка корректности конфигурации WireGuard.
    """
    with open(config_path, "r") as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith("Address =") and not " " in line.split("=")[1]:
            raise ValueError(f"Неправильный формат строки: {line.strip()}")

    log_debug("Конфигурация WireGuard прошла проверку.")
