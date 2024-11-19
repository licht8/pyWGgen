#!/usr/bin/env python3
# ip_management.py
## Скрипт для управления IP-адресами в проекте WireGuard

import ipaddress
from modules.utils import get_wireguard_subnet


def get_existing_ips(config_file):
    """
    Получить список всех IP-адресов из конфигурации сервера WireGuard.
    :param config_file: Путь к конфигурационному файлу WireGuard.
    :return: Список занятых IP-адресов.
    """
    try:
        with open(config_file, "r") as file:
            lines = file.readlines()
        existing_ips = []
        for line in lines:
            if line.strip().startswith("AllowedIPs"):
                ip = line.split("=")[-1].strip().split(",")[0]  # Берём только IPv4
                existing_ips.append(ip.split("/")[0])  # Убираем маску подсети
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

    # Лог отладки
    print(f"Существующие IP: {existing_ips}")
    print(f"Подсеть WireGuard: {subnet}")

    # Преобразуем подсеть в объект ip_network
    network = ipaddress.ip_network(subnet, strict=False)

    # Проходим по всем IP-адресам в подсети, начиная с первого доступного
    for ip in network.hosts():  # Исключает адреса сети и широковещательный
        ip_str = str(ip)
        if ip_str not in existing_ips:
            return ip_str, existing_ips

    # Если все IP-адреса заняты, выбрасываем исключение
    raise RuntimeError("Нет доступных IP-адресов в подсети WireGuard.")
