#!/usr/bin/env python3
# utils.py
## Содержит вспомогательные функции для работы с проектом wg_qr_generator.

import json
import os


def read_json(file_path):
    """
    Чтение данных из JSON-файла.
    :param file_path: Путь к JSON-файлу.
    :return: Содержимое файла как словарь.
    """
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def write_json(file_path, data):
    """
    Запись данных в JSON-файл.
    :param file_path: Путь к JSON-файлу.
    :param data: Данные для записи.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def get_wireguard_config_path():
    """
    Получение пути к текущему конфигурационному файлу WireGuard.
    :return: Путь к конфигурационному файлу.
    """
    return "/etc/wireguard/wg0.conf"


def parse_wireguard_config(config_path=None):
    """
    Чтение и разбор конфигурационного файла WireGuard.
    :param config_path: Путь к конфигурационному файлу.
    :return: Содержимое файла как строка.
    """
    if config_path is None:
        config_path = get_wireguard_config_path()

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"WireGuard конфигурационный файл не найден: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as file:
        return file.read()


def get_wireguard_subnet(config_path=None):
    """
    Извлечение подсети WireGuard из конфигурационного файла.
    :param config_path: Путь к конфигурационному файлу.
    :return: Подсеть в формате строки (например, "10.96.96.0/24").
    """
    if config_path is None:
        config_path = get_wireguard_config_path()

    config_content = parse_wireguard_config(config_path)
    for line in config_content.splitlines():
        if line.startswith("Address"):
            addresses = line.split('=')[1].strip().split(',')
            for address in addresses:
                if '/' in address and '.' in address:  # Убедимся, что это IPv4
                    return address
    raise ValueError("Не удалось найти подсеть WireGuard в конфигурационном файле.")
