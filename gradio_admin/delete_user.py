#!/usr/bin/env python3
# delete_user.py
## Скрипт для удаления пользователей из WireGuard и связанных записей.

import os
import json
import subprocess
from datetime import datetime
from modules.utils import read_json, write_json, get_wireguard_config_path


def log_debug(message):
    """Логирование отладочной информации."""
    print(f"[DEBUG] {datetime.now().isoformat()} - {message}")


def format_wireguard_config(config_path):
    """
    Приведение конфигурации WireGuard к корректному формату.
    Исправляет строки Address и дублирующиеся блоки.
    """
    log_debug(f"Форматируем файл конфигурации: {config_path}")
    with open(config_path, "r") as f:
        lines = f.readlines()

    formatted_lines = []
    seen_peers = set()
    for line in lines:
        if line.startswith("Address="):  # Исправляем строки с Address
            addresses = line.split("=")[1].strip().split(",")
            for address in addresses:
                formatted_lines.append(f"Address = {address.strip()}\n")
        elif line.startswith("[Peer]"):
            # Убираем дублирующиеся блоки [Peer]
            peer_start_index = len(formatted_lines)
            formatted_lines.append(line)
            seen_peers.add(peer_start_index)
        else:
            formatted_lines.append(line)

    with open(config_path, "w") as f:
        f.writelines(formatted_lines)
    log_debug("Форматирование файла завершено.")


def validate_wireguard_config(config_path):
    """
    Проверяет конфигурацию WireGuard на наличие ошибок.
    """
    log_debug(f"Проверяем конфигурацию WireGuard: {config_path}")
    try:
        subprocess.run(["wg-quick", "strip", config_path], check=True, text=True, stderr=subprocess.PIPE)
        log_debug("Конфигурация WireGuard прошла проверку.")
    except subprocess.CalledProcessError as e:
        log_debug(f"Ошибка проверки конфигурации: {e.stderr.strip()}")
        raise ValueError(f"Ошибка в файле конфигурации WireGuard: {e.stderr.strip()}")


def delete_user(username):
    """
    Удаление пользователя из конфигурации WireGuard и связанных файлов.
    """
    log_debug(f"Начало удаления пользователя: {username}")
    base_dir = os.getcwd()
    user_records_path = os.path.join(base_dir, "user", "data", "user_records.json")
    wg_config_path = get_wireguard_config_path()

    if not os.path.exists(user_records_path):
        log_debug("Файл user_records.json не найден.")
        return "❌ Файл user_records.json не найден."

    try:
        user_data = read_json(user_records_path)
        if username not in user_data:
            log_debug(f"Пользователь {username} не найден в user_records.json.")
            return f"❌ Пользователь {username} не найден."

        # Удаление записи пользователя
        user_info = user_data.pop(username)
        user_info["removed_at"] = datetime.now().isoformat()
        log_debug(f"Удалена запись пользователя: {user_info}")

        # Обновление записей пользователей
        write_json(user_records_path, user_data)

        # Удаление пользователя из конфигурации WireGuard
        if os.path.exists(wg_config_path):
            with open(wg_config_path, "r") as f:
                config_lines = f.readlines()

            updated_lines = []
            inside_peer_block = False
            current_block = []

            for line in config_lines:
                if line.strip() == "[Peer]":
                    if current_block and username not in "".join(current_block):
                        updated_lines.extend(current_block)
                    inside_peer_block = True
                    current_block = [line]
                    continue

                if inside_peer_block:
                    current_block.append(line)
                    if line.strip() == "":
                        inside_peer_block = False
                else:
                    updated_lines.append(line)

            if current_block and username not in "".join(current_block):
                updated_lines.extend(current_block)

            with open(wg_config_path, "w") as f:
                f.writelines(updated_lines)
            log_debug(f"Конфигурация WireGuard обновлена: {wg_config_path}")

            format_wireguard_config(wg_config_path)
            validate_wireguard_config(wg_config_path)

            subprocess.run(["wg", "syncconf", "wg0", wg_config_path], check=True)
            log_debug("Конфигурация WireGuard успешно синхронизирована.")

        return f"✅ Пользователь {username} успешно удалён."
    except subprocess.CalledProcessError as e:
        log_debug(f"Ошибка при синхронизации WireGuard: {e.stderr.strip()}")
        return f"❌ Ошибка при синхронизации WireGuard: {e.stderr.strip()}"
    except Exception as e:
        log_debug(f"Ошибка при удалении пользователя {username}: {str(e)}")
        return f"❌ Ошибка при удалении пользователя {username}: {str(e)}"
