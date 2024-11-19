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


def generate_ip(existing_ips, subnet="10.66.66.0"):
    """Генерирует новый IP-адрес в указанной подсети."""
    base_ip = ipaddress.IPv4Network(subnet, strict=False)
    for ip in base_ip.hosts():
        if str(ip) not in existing_ips:
            return f"{ip}/32", str(ip)
    raise RuntimeError("Нет доступных IP-адресов в подсети.")
