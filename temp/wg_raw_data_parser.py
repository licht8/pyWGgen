#!/usr/bin/env python3
# wg_raw_data_parser.py
# ==================================================
# Скрипт для сбора необработанных данных WireGuard из разных источников.
# Версия: 1.0 (2024-12-21)
# ==================================================
# Описание:
# Этот скрипт собирает данные из следующих источников:
# - Файл конфигурации `/etc/wireguard/wg0.conf`
# - Вывод команды `wg show`
# - Файл параметров `/etc/wireguard/params`
#
# Затем записывает все данные в один текстовый файл в сыром виде.
# ==================================================

import subprocess
import os
from pathlib import Path

# Установите пути к файлам
WG_CONFIG_FILE = "/etc/wireguard/wg0.conf"
WG_PARAMS_FILE = "/etc/wireguard/params"
OUTPUT_FILE = "wg_raw_data.txt"

def read_file(filepath):
    """Читает содержимое файла."""
    if not os.path.exists(filepath):
        return f"[ERROR] File not found: {filepath}\n"
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except Exception as e:
        return f"[ERROR] Unable to read file {filepath}: {e}\n"

def get_wg_status():
    """Получает состояние WireGuard через команду `wg show`."""
    try:
        output = subprocess.check_output(["wg", "show"], text=True)
        return output
    except subprocess.CalledProcessError as e:
        return f"[ERROR] Failed to execute `wg show`: {e}\n"
    except Exception as e:
        return f"[ERROR] Unexpected error while executing `wg show`: {e}\n"

def collect_raw_data():
    """Собирает данные из всех источников."""
    raw_data = []

    # Чтение конфигурационного файла
    raw_data.append("[WireGuard Configuration File]")
    raw_data.append(read_file(WG_CONFIG_FILE))

    # Вывод команды `wg show`
    raw_data.append("\n[WireGuard Status (`wg show`)]")
    raw_data.append(get_wg_status())

    # Чтение файла параметров
    raw_data.append("\n[WireGuard Parameters File]")
    raw_data.append(read_file(WG_PARAMS_FILE))

    return "\n".join(raw_data)

def save_to_file(data, output_file):
    """Сохраняет данные в текстовый файл."""
    try:
        with open(output_file, 'w') as file:
            file.write(data)
        print(f"Data successfully saved to {output_file}")
    except Exception as e:
        print(f"[ERROR] Failed to save data to {output_file}: {e}")

if __name__ == "__main__":
    # Собираем сырые данные
    raw_data = collect_raw_data()

    # Сохраняем данные в файл
    save_to_file(raw_data, OUTPUT_FILE)
