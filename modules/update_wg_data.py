#!/usr/bin/env python3
"""
modules/update_wg_data.py

Скрипт для обновления данных WireGuard:
- Обновляет трафик и состояние пользователей.
- Логирует подключения и общий трафик.
- Обновляет JSON с историей пользователей.

Должен запускаться периодически.
"""

import os
import subprocess
import json
from datetime import datetime

# Пути к файлам
WG_CONFIG_PATH = "/etc/wireguard/wg0.conf"
JSON_LOG_PATH = "/root/pyWGgen/wg_qr_generator/logs/wg_users.json"
TEXT_LOG_PATH = "/root/pyWGgen/wg_qr_generator/logs/wg_activity.log"
DEBUG_LOG_PATH = "/root/pyWGgen/wg_qr_generator/logs/debug.log"

def log_debug(message):
    """Логирует отладочные сообщения в debug.log."""
    with open(DEBUG_LOG_PATH, "a") as debug_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        debug_file.write(f"[{timestamp}] {message}\n")


def parse_wg_show():
    """Считывает и парсит вывод команды `wg`."""
    try:
        output = subprocess.check_output(["wg"], text=True)
        log_debug("Команда `wg` выполнена успешно.")
    except subprocess.CalledProcessError as e:
        log_debug(f"Ошибка при выполнении `wg`: {e}")
        return None

    peers = {}
    current_peer = None

    for line in output.splitlines():
        if line.startswith("peer:"):
            current_peer = line.split(":")[1].strip()
            peers[current_peer] = {"transfer": {"received": "0 B", "sent": "0 B"}, "latest_handshake": None}
        elif line.strip().startswith("transfer:"):
            parts = line.strip().split(",")
            received = parts[0].split()[1]
            sent = parts[1].split()[1]
            peers[current_peer]["transfer"] = {"received": received, "sent": sent}
        elif line.strip().startswith("latest handshake:"):
            handshake = line.split(":")[1].strip()
            peers[current_peer]["latest_handshake"] = handshake

    log_debug(f"Данные `wg show`: {peers}")
    return peers


def parse_wg_conf():
    """Считывает конфигурацию WireGuard для получения соответствия пользователей."""
    try:
        with open(WG_CONFIG_PATH, "r") as f:
            config = f.read()
        log_debug("Конфигурация WireGuard прочитана успешно.")
    except FileNotFoundError:
        log_debug(f"Файл {WG_CONFIG_PATH} не найден.")
        return None

    users = {}
    current_peer = None

    for line in config.splitlines():
        if line.strip().startswith("[Peer]"):
            current_peer = None
        elif line.strip().startswith("PublicKey ="):
            current_peer = line.split("=")[1].strip()
            users[current_peer] = {"username": None, "allowed_ips": None}
        elif line.strip().startswith("#"):
            if current_peer:
                users[current_peer]["username"] = line.strip("#").strip()
        elif line.strip().startswith("AllowedIPs ="):
            if current_peer:
                users[current_peer]["allowed_ips"] = line.split("=")[1].strip()

    log_debug(f"Пользователи из конфигурации: {users}")
    return users


def parse_size(size_str):
    """Парсит строку размера (например, '4.88 KiB') в байты."""
    size, unit = size_str.split()
    size = float(size)
    unit = unit.lower()
    multiplier = {
        "b": 1,
        "kib": 1024,
        "mib": 1024**2,
        "gib": 1024**3
    }
    return int(size * multiplier.get(unit, 1))


def format_size(size_bytes):
    """Форматирует размер в байтах в удобочитаемый вид."""
    for unit in ["B", "KiB", "MiB", "GiB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} GiB"


def update_data():
    """Обновляет JSON и текстовый лог на основе текущих данных `wg`."""
    log_debug("=== Начало обновления данных ===")

    wg_show = parse_wg_show()
    wg_conf = parse_wg_conf()

    if not wg_show or not wg_conf:
        log_debug("Ошибка: данные `wg show` или конфигурации не загружены.")
        return

    # Загружаем или создаем JSON с историей
    if os.path.exists(JSON_LOG_PATH):
        with open(JSON_LOG_PATH, "r") as f:
            history = json.load(f)
        log_debug("JSON-файл с историей загружен.")
    else:
        history = {"users": {}}
        log_debug("Создан новый JSON-файл с историей.")

    for peer, data in wg_conf.items():
        username = data["username"]
        allowed_ips = data["allowed_ips"]
        transfer = wg_show.get(peer, {}).get("transfer", {"received": "0 B", "sent": "0 B"})
        latest_handshake = wg_show.get(peer, {}).get("latest_handshake", None)

        user_data = history["users"].get(username, {
            "peer": peer,
            "endpoints": [],
            "allowed_ips": allowed_ips,
            "total_transfer": {"received": "0 B", "sent": "0 B"},
            "last_handshake": None,
            "status": "inactive"
        })

        # Логируем данные пользователя
        log_debug(f"Пользователь {username}: до обновления: {user_data}")

        # Обновляем статус и handshake
        if latest_handshake:
            user_data["last_handshake"] = latest_handshake
            user_data["status"] = "active"
        else:
            user_data["status"] = "inactive"

        # Обновляем трафик
        new_received = parse_size(transfer["received"])
        new_sent = parse_size(transfer["sent"])
        old_received = parse_size(user_data["total_transfer"]["received"])
        old_sent = parse_size(user_data["total_transfer"]["sent"])

        if new_received < old_received or new_sent < old_sent:
            new_received += old_received
            new_sent += old_sent

        user_data["total_transfer"] = {
            "received": format_size(new_received),
            "sent": format_size(new_sent)
        }

        endpoint = wg_show.get(peer, {}).get("endpoint", None)
        if endpoint and endpoint not in user_data["endpoints"]:
            user_data["endpoints"].append(endpoint)

        # Сохраняем в историю
        history["users"][username] = user_data

        log_debug(f"Пользователь {username}: после обновления: {user_data}")

    # Сохраняем обновленный JSON
    with open(JSON_LOG_PATH, "w") as f:
        json.dump(history, f, indent=4)
    log_debug("JSON-файл успешно обновлен.")

    log_debug("=== Обновление данных завершено ===")


if __name__ == "__main__":
    update_data()
