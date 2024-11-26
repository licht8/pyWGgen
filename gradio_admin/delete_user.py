#!/usr/bin/env python3
# delete_user.py
# Скрипт для удаления пользователей в проекте wg_qr_generator

import os
import subprocess
from datetime import datetime
from modules.utils import read_json, write_json, get_wireguard_config_path, log_debug


def delete_user(username):
    """
    Удаление пользователя из конфигурации WireGuard и связанных файлов.
    :param username: Имя пользователя для удаления.
    :return: Сообщение о результате операции.
    """
    base_dir = os.getcwd()
    user_records_path = os.path.join(base_dir, "user", "data", "user_records.json")
    wg_config_path = get_wireguard_config_path()

    log_debug(f"Начало удаления пользователя: {username}")

    if not os.path.exists(user_records_path):
        log_debug(f"❌ Файл user_records.json не найден: {user_records_path}")
        return "❌ Файл user_records.json не найден."

    try:
        # Чтение данных пользователей
        user_data = read_json(user_records_path)
        log_debug(f"Прочитаны данные пользователей: {user_data}")

        if username not in user_data:
            log_debug(f"❌ Пользователь {username} не найден в user_records.json")
            return f"❌ Пользователь {username} не найден."

        # Удаление записи пользователя
        user_info = user_data.pop(username)
        user_info["removed_at"] = datetime.now().isoformat()
        write_json(user_records_path, user_data)
        log_debug(f"Записи пользователей обновлены: {user_records_path}")

        # Извлечение публичного ключа пользователя
        public_key = extract_public_key(username, wg_config_path)
        if not public_key:
            log_debug(f"❌ Публичный ключ пользователя {username} не найден.")
            return f"❌ Публичный ключ пользователя {username} не найден."

        # Удаление пользователя из WireGuard
        subprocess.run(["sudo", "wg", "set", "wg0", "peer", public_key, "remove"], check=True)
        log_debug(f"Пользователь {username} с публичным ключом {public_key} удален из WireGuard.")

        # Обновление конфигурации WireGuard
        remove_peer_from_config(public_key, wg_config_path, username)
        log_debug(f"Конфигурация WireGuard обновлена: {wg_config_path}")

        return f"✅ Пользователь {username} успешно удалён."
    except Exception as e:
        log_debug(f"Ошибка при удалении пользователя {username}: {str(e)}")
        return f"❌ Ошибка при удалении пользователя {username}: {str(e)}"


def extract_public_key(username, config_path):
    """
    Извлечение публичного ключа пользователя из конфигурации WireGuard.
    :param username: Имя пользователя.
    :param config_path: Путь к конфигурационному файлу WireGuard.
    :return: Публичный ключ пользователя.
    """
    log_debug(f"Ищем публичный ключ пользователя {username} в {config_path}.")
    try:
        with open(config_path, "r") as f:
            lines = f.readlines()

        found_username = False
        for line in lines:
            if username in line:
                found_username = True
            elif found_username and line.strip().startswith("PublicKey"):
                public_key = line.split("=", 1)[1].strip()
                log_debug(f"Публичный ключ пользователя {username}: {public_key}")
                return public_key
        log_debug(f"Публичный ключ пользователя {username} не найден в {config_path}.")
        return None
    except Exception as e:
        log_debug(f"Ошибка при поиске публичного ключа: {str(e)}")
        return None


def remove_peer_from_config(public_key, config_path, client_name):
    """
    Удаление записи [Peer] и связанного комментария из конфигурационного файла WireGuard.
    Удаляет комментарий и 4 строки, начиная с него.
    :param public_key: Публичный ключ пользователя.
    :param config_path: Путь к конфигурационному файлу WireGuard.
    :param client_name: Имя клиента.
    """
    log_debug(f"Начало удаления [Peer] для {client_name} с ключом {public_key} из {config_path}.")

    try:
        with open(config_path, "r") as f:
            lines = f.readlines()

        updated_lines = []
        skip_lines = 0  # Счетчик строк для пропуска

        for i, line in enumerate(lines):
            # Если найден комментарий клиента
            if line.strip() == f"### Client {client_name}":
                log_debug(f"Найден комментарий: {line.strip()} на строке {i}. Удаляем блок.")
                skip_lines = 5  # Удаляем 5 строк начиная с этого момента
                continue

            # Пропуск строк, связанных с удаляемым блоком
            if skip_lines > 0:
                log_debug(f"Пропускаем строку {i}: {line.strip()}")
                skip_lines -= 1
                continue

            # Сохранение остальных строк
            updated_lines.append(line)

        # Запись обновленной конфигурации
        with open(config_path, "w") as f:
            f.writelines(updated_lines)

        log_debug(f"Удаление блока для {client_name} завершено. Конфигурация обновлена.")
    except Exception as e:
        log_debug(f"Ошибка при обновлении конфигурации: {str(e)}")
