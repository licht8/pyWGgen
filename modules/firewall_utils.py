#!/usr/bin/env python3
# modules/firewall_utils.py
# Функции для управления портами через firewalld

import subprocess
import psutil
from modules.port_manager import handle_port_conflict

def get_external_ip():
    """Получает внешний IP-адрес."""
    try:
        return subprocess.check_output(["curl", "-s", "https://ipinfo.io/ip"], text=True).strip()
    except subprocess.CalledProcessError:
        return colored("N/A ❌", "red")

def open_firewalld_port(port):
    """Открывает порт в firewalld."""
    # Модуль для управления портами и разрешения конфликтов
    # Проверяет, занят ли порт, и предлагает действия пользователю.
    handle_port_conflict(port)
    print(f" 🔓  Открытие порта {port} через firewalld...\n")
    subprocess.run(["firewall-cmd", "--add-port", f"{port}/tcp", "--permanent"])
    subprocess.run(["firewall-cmd", "--reload"])

def close_firewalld_port(port):
    """Закрывает порт в firewalld."""
    print(f" 🔒  Закрытие порта {port} через firewalld...\n")
    subprocess.run(["firewall-cmd", "--remove-port", f"{port}/tcp", "--permanent"])
    subprocess.run(["firewall-cmd", "--reload"])
