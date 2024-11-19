#!/usr/bin/env python3
# ip_management.py
## Скрипт для управления IP-адресами в проекте WireGuard

import ipaddress


def get_existing_ips(config_file):
    """Получить список всех IP-адресов из конфигурации сервера WireGuard."""
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

    # Получаем базовый IP-адрес подсети (например, 10.96.96.0/24 -> 10.96.96.)
    prefix = ".".join(subnet.split(".")[:3]) + "."

    # Проверяем возможные адреса
    for i in range(2, 255):  # 10.96.96.2 - 10.96.96.254
        candidate = f"{prefix}{i}"
        if candidate not in existing_ips and f"{candidate}/32" not in existing_ips:
            return candidate, existing_ips

    raise RuntimeError("Нет доступных IP-адресов в подсети WireGuard.")
