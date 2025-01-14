#!/usr/bin/env python3
# modules/traffic_updater.py

import json
import os
import subprocess
from settings import SERVER_WG_NIC  # Импорт интерфейса WireGuard из настроек
from settings import USER_DB_PATH

def update_traffic_data():
    """
    Обновляет данные о текущем и общем трафике пользователей, записывая одинаковые значения для transfer и total_transfer в user_records.json.
    """
    if not os.path.exists(USER_DB_PATH):
        print(f"Файл {USER_DB_PATH} не найден.")
        return

    # Загрузка данных пользователей
    with open(USER_DB_PATH, "r") as f:
        user_records = json.load(f)

    try:
        # Получение данных о трафике из WireGuard
        output = subprocess.check_output(["wg", "show", SERVER_WG_NIC, "transfer"], text=True)
        lines = output.strip().split("\n")

        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                public_key = parts[0]
                received = int(parts[1])  # Текущие данные
                sent = int(parts[2])

                # Поиск пользователя по public_key
                for username, user_data in user_records.items():
                    if user_data.get("public_key") == public_key:
                        # Обновление поля transfer
                        transfer_str = f"{received / (1024 ** 2):.2f} MiB received, {sent / (1024 ** 2):.2f} MiB sent"
                        user_data["transfer"] = transfer_str
                        user_data["total_transfer"] = transfer_str  # Дублируем значение
                        break

    except Exception as e:
        print(f"Ошибка при обновлении трафика: {e}")
        return

    # Сохранение обновлённых данных
    with open(USER_DB_PATH, "w") as f:
        json.dump(user_records, f, indent=4)
