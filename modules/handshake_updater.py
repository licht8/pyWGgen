#!/usr/bin/env python3
# modules/handshake_updater.py

import os
import json
import subprocess
from datetime import datetime
from settings import USER_DB_PATH, SERVER_WG_NIC

def get_latest_handshakes(interface):
    """
    Извлекает информацию о последнем рукопожатии пользователей WireGuard.
    :param interface: Имя интерфейса WireGuard.
    :return: Словарь {public_key: last_handshake}.
    """
    try:
        output = subprocess.check_output(["wg", "show", interface, "latest-handshakes"], text=True)
        lines = output.strip().split("\n")
        handshakes = {}

        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                public_key = parts[0]
                timestamp = int(parts[1])
                handshakes[public_key] = convert_handshake_timestamp(timestamp)

        return handshakes
    except Exception as e:
        print(f"Ошибка при получении информации о рукопожатиях: {e}")
        return {}

def convert_handshake_timestamp(timestamp):
    """
    Преобразует Unix timestamp в читаемый формат.
    :param timestamp: Метка времени (Unix timestamp).
    :return: Читаемая строка даты и времени в формате UTC или 'Never', если рукопожатие не было установлено (timestamp равен 0).
    """
    if timestamp == 0:
        return "Never"
    return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")

def update_handshakes(user_records_path, interface):
    """
    Обновляет информацию о последнем рукопожатии пользователей в user_records.json.
    :param user_records_path: Путь к файлу user_records.json.
    :param interface: Имя интерфейса WireGuard.
    """
    if not os.path.exists(user_records_path):
        print(f"Файл {user_records_path} не найден.")
        return

    with open(user_records_path, "r") as f:
        user_records = json.load(f)

    handshakes = get_latest_handshakes(interface)

    for username, user_data in user_records.items():
        public_key = user_data.get("public_key")
        if public_key in handshakes:
            user_data["last_handshake"] = handshakes[public_key]

    with open(user_records_path, "w") as f:
        json.dump(user_records, f, indent=4)

    print("Информация о последнем рукопожатии успешно обновлена.")

if __name__ == "__main__":
    # Обновление рукопожатий для пользователей
    update_handshakes(USER_DB_PATH, SERVER_WG_NIC)
