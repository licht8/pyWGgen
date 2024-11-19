#!/usr/bin/env python3
# ip_management.py
## Скрипт для управления IP-адресами в проекте WireGuard.

import ipaddress
from modules.utils import get_wireguard_subnet  # Импорт функции из utils


def get_existing_ips(config_file):
    """
    Получить список всех IP-адресов из конфигурации сервера WireGuard.
    :param config_file: Путь к конфигурационному файлу WireGuard.
    :return: Список существующих IP-адресов.
    """
    try:
        with open(config_file, "r") as file:
            lines = file.readlines()
        existing_ips = []
        for line in lines:
            if line.strip().startswith("AllowedIPs"):
                ip = line.split("=")[-1].strip().split(",")[0]  # Берём только IPv4
                existing_ips.append(ip)
        return existing_ips
    except FileNotFoundError:
        return []


def generate_ip(config_file):
    """
    Генерация нового IP-адреса в подсети WireGuard.
    :param config_file: Путь к файлу конфигурации WireGuard.
    :return: Новый IP-адрес и список существующих адресов.
    """
    existing_ips = get_existing_ips(config_file)
    subnet = get_wireguard_subnet()

    # Получаем базовый IP-адрес подсети
    network = ipaddress.ip_network(subnet, strict=False)

    # Проверяем возможные адреса
    for candidate in network.hosts():
        candidate_str = str(candidate)
        if candidate_str not in existing_ips and f"{candidate_str}/32" not in existing_ips:
            return candidate_str, existing_ips

    raise RuntimeError("Нет доступных IP-адресов в подсети WireGuard.")
