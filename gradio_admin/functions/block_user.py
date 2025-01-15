# gradio_admin/functions/block_user.py

import json
import subprocess  # Для управления VPN через системные команды
from settings import USER_DB_PATH, WG_CONFIG_PATH  # Путь к JSON и конфигурации WireGuard

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
    2. Отключает VPN (например, через WireGuard).
    """
    records = load_user_records()
    if username not in records:
        return False, f"User '{username}' not found."
    
    # Обновляем статус
    records[username]["status"] = "blocked"
    
    # Сохраняем обновления в JSON
    if not save_user_records(records):
        return False, f"Failed to update JSON for user '{username}'."
    
    # Отключаем VPN для пользователя
    result = disable_vpn_for_user(username)
    if result:
        return True, f"User '{username}' has been blocked and VPN access revoked."
    else:
        return False, f"Failed to revoke VPN access for user '{username}'."

def unblock_user(username):
    """
    Разблокирует пользователя:
    1. Обновляет статус в JSON на 'active'.
    2. Включает VPN (например, через WireGuard).
    """
    records = load_user_records()
    if username not in records:
        return False, f"User '{username}' not found."
    
    # Обновляем статус
    records[username]["status"] = "active"
    
    # Сохраняем обновления в JSON
    if not save_user_records(records):
        return False, f"Failed to update JSON for user '{username}'."
    
    # Включаем VPN для пользователя
    result = enable_vpn_for_user(username)
    if result:
        return True, f"User '{username}' has been unblocked and VPN access restored."
    else:
        return False, f"Failed to restore VPN access for user '{username}'."

def disable_vpn_for_user(username):
    """
    Отключает VPN для пользователя.
    Предполагается, что VPN управляется через WireGuard.
    """
    try:
        # Например, отключаем пользователя через `wg` команду
        command = f"wg set {WG_CONFIG_PATH} peer {username} remove"
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to disable VPN for user '{username}': {e}")
        return False

def enable_vpn_for_user(username):
    """
    Включает VPN для пользователя.
    """
    try:
        # Например, восстанавливаем конфигурацию пользователя через WireGuard
        command = f"wg set {WG_CONFIG_PATH} peer {username} allowed-ips 0.0.0.0/0"
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to enable VPN for user '{username}': {e}")
        return False