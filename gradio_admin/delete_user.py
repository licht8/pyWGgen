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
    log_debug(f"Удаляем [Peer] с ключом {public_key} из {config_path}.")
    with open(config_path, "r") as f:
        lines = f.readlines()

    updated_lines = []
    inside_peer_block = False
    remove_comment = False

    for line in lines:
        if line.strip().startswith("### Client "):
            # Если мы нашли комментарий клиента
            if remove_comment:
                # Пропускаем строку комментария, связанную с предыдущим [Peer]
                remove_comment = False
                continue
            else:
                # Сохраняем комментарий, если не связан с удалением
                updated_lines.append(line)
                continue

        if line.strip() == f"PublicKey = {public_key}":
            # Найден блок с указанным публичным ключом
            inside_peer_block = True
            remove_comment = True
            continue

        if inside_peer_block and (line.strip() == "" or line.strip().startswith("[Peer]")):
            # Конец или начало следующего блока [Peer]
            inside_peer_block = False
            continue

        if not inside_peer_block:
            # Сохраняем строки, если они не в удаляемом блоке
            updated_lines.append(line)

    # Удаляем возможные пустые строки между блоками
    cleaned_lines = [line for i, line in enumerate(updated_lines) if not (line.strip() == "" and (i == 0 or updated_lines[i - 1].strip() == ""))]

    with open(config_path, "w") as f:
        f.writelines(cleaned_lines)
    log_debug(f"Удаление [Peer] с ключом {public_key} и комментария завершено.")
