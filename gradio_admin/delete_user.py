#!/usr/bin/env python3
# delete_user.py
import os
import subprocess
from datetime import datetime
from modules.utils import read_json, write_json, get_wireguard_config_path, log_debug

def delete_user(username):
    """
    Удаление пользователя из конфигурации WireGuard и связанных файлов.
    """
    base_dir = os.getcwd()
    user_records_path = os.path.join(base_dir, "user", "data", "user_records.json")
    wg_config_path = get_wireguard_config_path()

    log_debug(f"Начало удаления пользователя: {username}")

    if not os.path.exists(user_records_path):
        log_debug(f"❌ Файл user_records.json не найден: {user_records_path}")
        return "❌ Файл user_records.json не найден."

    try:
        user_data = read_json(user_records_path)
        log_debug(f"Прочитаны данные пользователей: {user_data}")

        if username not in user_data:
            log_debug(f"❌ Пользователь {username} не найден в user_records.json")
            return f"❌ Пользователь {username} не найден."

        user_info = user_data.pop(username)
        user_info["removed_at"] = datetime.now().isoformat()

        # Обновляем JSON
        write_json(user_records_path, user_data)
        log_debug(f"Записи пользователей обновлены: {user_records_path}")

        # Извлекаем публичный ключ
        public_key = extract_public_key(username, wg_config_path)
        if not public_key:
            log_debug(f"❌ Публичный ключ пользователя {username} не найден.")
            return f"❌ Публичный ключ пользователя {username} не найден."

        # Удаляем пользователя из WireGuard
        subprocess.run(["sudo", "wg", "set", "wg0", "peer", public_key, "remove"], check=True)
        log_debug(f"Пользователь {username} с публичным ключом {public_key} удален из WireGuard.")

        # Обновляем конфигурацию
        remove_peer_from_config(public_key, wg_config_path)
        log_debug(f"Конфигурация WireGuard обновлена: {wg_config_path}")

        return f"✅ Пользователь {username} успешно удалён."
    except Exception as e:
        log_debug(f"Ошибка при удалении пользователя {username}: {str(e)}")
        return f"❌ Ошибка при удалении пользователя {username}: {str(e)}"


def extract_public_key(username, config_path):
    """
    Извлечение публичного ключа пользователя из конфигурации WireGuard.
    """
    log_debug(f"Ищем публичный ключ пользователя {username} в {config_path}.")
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


def remove_peer_from_config(public_key, config_path, client_name):
    """
    Удаление записи [Peer] и связанного комментария из конфигурационного файла WireGuard.
    Удаляет комментарий и 4 строки, начиная с него.
    """
    log_debug(f"Начало удаления [Peer] для {client_name} с ключом {public_key} из {config_path}.")

    with open(config_path, "r") as f:
        lines = f.readlines()

    updated_lines = []
    skip_lines = 0  # Счетчик строк для пропуска

    for i, line in enumerate(lines):
        # Если нашли комментарий клиента
        if line.strip() == f"### Client {client_name}":
            log_debug(f"Найден комментарий: {line.strip()} на строке {i}. Удаляем блок.")
            skip_lines = 5  # Удаляем 5 строк начиная с этого момента
            continue

        # Пропускаем строки, связанные с удаляемым блоком
        if skip_lines > 0:
            log_debug(f"Пропускаем строку {i}: {line.strip()}")
            skip_lines -= 1
            continue

        # Сохраняем остальные строки
        updated_lines.append(line)

    with open(config_path, "w") as f:
        f.writelines(updated_lines)

    log_debug(f"Удаление блока для {client_name} завершено. Конфигурация обновлена.")
