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


def remove_peer_from_config(public_key, config_path):
    """
    Удаление записи [Peer] с указанным публичным ключом и соответствующего комментария из конфигурационного файла WireGuard.
    Также удаляет пустые блоки [Peer] и связанные комментарии.
    """
    log_debug(f"Начало удаления [Peer] с ключом {public_key} из {config_path}.")

    with open(config_path, "r") as f:
        lines = f.readlines()

    updated_lines = []
    inside_peer_block = False
    remove_comment = False

    for i, line in enumerate(lines):
        log_debug(f"Обрабатывается строка {i}: {line.strip()}")

        # Если это комментарий клиента
        if line.strip().startswith("### Client "):
            log_debug(f"Найден комментарий клиента: {line.strip()}")
            if remove_comment:
                log_debug(f"Комментарий '{line.strip()}' будет удален, так как связан с удаляемым [Peer].")
                remove_comment = False
                continue
            else:
                log_debug(f"Комментарий '{line.strip()}' сохранен, так как не связан с удаляемым [Peer].")
                updated_lines.append(line)
                continue

        # Если строка содержит PublicKey
        if line.strip() == f"PublicKey = {public_key}":
            log_debug(f"Найден публичный ключ: {line.strip()}, начинаем удаление блока.")
            inside_peer_block = True
            remove_comment = True
            continue

        # Конец или начало следующего блока
        if inside_peer_block and (line.strip() == "" or line.strip().startswith("[Peer]")):
            log_debug(f"Конец блока для ключа {public_key}, блок будет удален.")
            inside_peer_block = False
            continue

        # Сохраняем строку, если не внутри удаляемого блока
        if not inside_peer_block:
            log_debug(f"Строка '{line.strip()}' сохранена.")
            updated_lines.append(line)

    # Удаляем возможные пустые строки между блоками
    cleaned_lines = []
    for i, line in enumerate(updated_lines):
        if line.strip() == "" and (i == 0 or updated_lines[i - 1].strip() == ""):
            log_debug(f"Удаление лишней пустой строки на позиции {i}.")
            continue
        cleaned_lines.append(line)

    with open(config_path, "w") as f:
        f.writelines(cleaned_lines)
    log_debug(f"Удаление [Peer] с ключом {public_key} завершено. Конфигурация обновлена.")
