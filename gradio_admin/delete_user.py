#!/usr/bin/env python3
# delete_user.py
## Скрипт для удаления пользователей из WireGuard и связанных записей.

import os
import json
import subprocess
from datetime import datetime
from modules.utils import read_json, write_json, get_wireguard_config_path, log_debug

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

    for line in lines:
        # Исправление строки Address
        if line.strip().startswith("Address="):
            addresses = line.split("=")[1].strip().split(",")
            for address in addresses:
                formatted_lines.append(f"Address = {address.strip()}\n")
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

    with open(config_path, "w") as f:
        f.writelines(formatted_lines)
    log_debug("Форматирование файла завершено.")


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
        log_debug(f"Удалена запись пользователя: {user_info}")

        # Удаление пользователя из конфигурации WireGuard
        if os.path.exists(wg_config_path):
            with open(wg_config_path, "r") as f:
                config_lines = f.readlines()
            updated_lines = [line for line in config_lines if username not in line]
            with open(wg_config_path, "w") as f:
                f.writelines(updated_lines)
            log_debug(f"Конфигурация WireGuard обновлена: {wg_config_path}")

        # Форматирование файла конфигурации
        format_wireguard_config(wg_config_path)

        # Проверка конфигурации WireGuard
        try:
            subprocess.run(["wg", "showconf", "wg0"], check=True, capture_output=True)
            log_debug(f"Конфигурация WireGuard прошла проверку.")
        except subprocess.CalledProcessError as e:
            log_debug(f"Ошибка проверки конфигурации: {e.stderr.decode().strip()}")
            return f"❌ Ошибка в файле конфигурации WireGuard: {e.stderr.decode().strip()}"

        # Применение синхронизации
        try:
            subprocess.run(["wg", "syncconf", "wg0", wg_config_path], check=True)
            log_debug("Синхронизация WireGuard успешно выполнена.")
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode().strip() if e.stderr else "Unknown error"
            log_debug(f"Ошибка при синхронизации WireGuard: {error_message}")
            return f"❌ Ошибка при синхронизации WireGuard: {error_message}"

        return f"✅ Пользователь {username} успешно удалён."
    except Exception as e:
        log_debug(f"Ошибка при удалении пользователя {username}: {str(e)}")
        return f"❌ Ошибка при удалении пользователя {username}: {str(e)}"
