#!/usr/bin/env python3
# modules/traffic_updater.py

import json
import os
import subprocess
from settings import SERVER_WG_NIC  # Импорт интерфейса WireGuard из настроек

def update_traffic_data(user_records_path):
    """
    Обновляет данные о трафике пользователей в user_records.json.
    :param user_records_path: Путь к файлу user_records.json
    """
    if not os.path.exists(user_records_path):
        print(f"Файл {user_records_path} не найден.")
        return

    # Загрузка текущих записей пользователей
    with open(user_records_path, "r") as f:
        user_records = json.load(f)

    # Получение данных о трафике из WireGuard
    try:
        # Используем динамический интерфейс WireGuard
        output = subprocess.check_output(["wg", "show", SERVER_WG_NIC, "transfer"], text=True)
        lines = output.strip().split("\n")

        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                public_key = parts[0]
                received = int(parts[1])
                sent = int(parts[2])

                # Поиск пользователя по public_key
                for username, user_data in user_records.items():
                    if user_data.get("public_key") == public_key:
                        # Текущий трафик
                        current_transfer = f"{received / (1024 ** 2):.2f} MiB received, {sent / (1024 ** 2):.2f} MiB sent"
                        user_data["transfer"] = current_transfer

                        # Накопленный трафик
                        total_transfer = user_data.get("total_transfer", "0.0 KiB")
                        total_rx, total_tx = parse_transfer(total_transfer)
                        total_rx += received
                        total_tx += sent
                        user_data["total_transfer"] = f"{total_rx / (1024 ** 2):.2f} MiB received, {total_tx / (1024 ** 2):.2f} MiB sent"

                        break

    except Exception as e:
        print(f"Ошибка при обновлении трафика: {e}")
        return

    # Сохранение обновлённых данных
    with open(user_records_path, "w") as f:
        json.dump(user_records, f, indent=4)

def parse_transfer(transfer_str):
    """
    Парсит строку трафика в байты.
    :param transfer_str: строка вида '123.45 MiB received, 67.89 MiB sent'
    :return: (received_bytes, sent_bytes)
    """
    try:
        parts = transfer_str.replace("received", "").replace("sent", "").replace(",", "").split()
        received = float(parts[0]) * (1024 ** 2)
        sent = float(parts[2]) * (1024 ** 2)
        return int(received), int(sent)
    except Exception:
        return 0, 0