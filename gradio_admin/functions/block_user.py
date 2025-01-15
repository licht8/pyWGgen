# gradio_admin/functions/block_user.py

import json
import subprocess  # Для управления VPN через системные команды
from settings import USER_DB_PATH, SERVER_CONFIG_FILE  # Путь к JSON и конфигурации WireGuard
from settings import SERVER_WG_NIC

def load_user_records():
    """Загружает записи пользователей из JSON."""
    try:
        with open(USER_DB_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"[ERROR] Failed to load user records: {e}")
        return {}

def save_user_records(records):
    """Сохраняет записи пользователей в JSON."""
    try:
        with open(USER_DB_PATH, "w") as f:
            json.dump(records, f, indent=4)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save user records: {e}")
        return False

def block_user(username):
    """
    Блокирует пользователя:
    1. Обновляет статус в JSON на 'blocked'.
    2. Удаляет пользователя из конфигурации WireGuard.
    """
    records = load_user_records()
    if username not in records:
        return False, f"User '{username}' not found."
    
    # Обновляем статус в JSON
    records[username]["status"] = "blocked"
    if not save_user_records(records):
        return False, f"Failed to update JSON for user '{username}'."

    # Удаляем пользователя из конфигурации
    if not update_wireguard_config(username, block=True):
        return False, f"Failed to block VPN access for user '{username}'."

    return True, f"User '{username}' has been blocked and VPN access revoked."

def unblock_user(username):
    """
    Разблокирует пользователя:
    1. Обновляет статус в JSON на 'active'.
    2. Восстанавливает пользователя в конфигурации WireGuard.
    """
    records = load_user_records()
    if username not in records:
        return False, f"User '{username}' not found."
    
    # Обновляем статус в JSON
    records[username]["status"] = "active"
    if not save_user_records(records):
        return False, f"Failed to update JSON for user '{username}'."

    # Восстанавливаем пользователя в конфигурации
    if not update_wireguard_config(username, block=False):
        return False, f"Failed to restore VPN access for user '{username}'."

    return True, f"User '{username}' has been unblocked and VPN access restored."

def update_wireguard_config(username, block=True):
    """
    Обновляет конфигурационный файл WireGuard.
    1. Если block=True, комментирует весь блок [Peer] для пользователя.
    2. Если block=False, восстанавливает блок [Peer].
    """
    try:
        with open(SERVER_CONFIG_FILE, "r") as f:
            config_lines = f.readlines()

        updated_lines = []
        in_peer_block = False
        peer_belongs_to_user = False

        for line in config_lines:
            stripped_line = line.strip()

            # Начало нового блока [Peer]
            if stripped_line == "[Peer]":
                if in_peer_block:
                    # Если мы в предыдущем блоке, завершаем его
                    in_peer_block = False
                    peer_belongs_to_user = False

                in_peer_block = True
                updated_lines.append(line)
                continue

            # Проверка, принадлежит ли текущий блок пользователю
            if in_peer_block and "PublicKey" in stripped_line and username in stripped_line:
                peer_belongs_to_user = True

            # Обработка строк внутри блока [Peer]
            if in_peer_block and peer_belongs_to_user:
                if block:
                    # Комментируем все строки текущего блока
                    if not line.startswith("#"):
                        updated_lines.append(f"# {line}")
                    else:
                        updated_lines.append(line)  # Строка уже закомментирована
                else:
                    # Убираем комментарии
                    if line.startswith("# "):
                        updated_lines.append(line[2:])
                    else:
                        updated_lines.append(line)  # Строка уже разблокирована
                continue

            # Конец блока [Peer] (пустая строка)
            if in_peer_block and stripped_line == "":
                in_peer_block = False
                peer_belongs_to_user = False

            # Все остальные строки
            updated_lines.append(line)

        # Сохраняем обновлённый конфигурационный файл
        with open(SERVER_CONFIG_FILE, "w") as f:
            f.writelines(updated_lines)

        # Синхронизация WireGuard
        sync_command = f'wg syncconf "{SERVER_WG_NIC}" <(wg-quick strip "{SERVER_WG_NIC}")'
        subprocess.run(sync_command, shell=True, check=True, executable='/bin/bash')
        print(f"WireGuard синхронизирован для интерфейса {SERVER_WG_NIC}")

        return True
    except Exception as e:
        print(f"[ERROR] Failed to update WireGuard config: {e}")
        return False