#!/usr/bin/env python3
# modules/firewall_utils.py
# Функции для управления портами через firewalld

import subprocess
import psutil
from modules.port_manager import handle_port_conflict

import socket
import subprocess

def get_external_ip():
    """
    Получает внешний IP-адрес через внутренние настройки или сетевые интерфейсы.

    :return: Внешний IP-адрес (строка) или сообщение об ошибке.
    """
    try:
        # Попробуем определить внешний IP через стандартные сетевые интерфейсы
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Подключаемся к публичному DNS-серверу Google для определения IP
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]  # Получаем IP-адрес из сокета
    except OSError as e:
        return f"N/A ❌ (Ошибка: {e})"

def open_firewalld_port(port):
    """Открывает порт в firewalld."""
    # Модуль для управления портами и разрешения конфликтов
    # Проверяет, занят ли порт, и предлагает действия пользователю.
    handle_port_conflict(port)
    print(f" 🔓  Открытие порта {port} через firewalld...\n")
    subprocess.run(["firewall-cmd", "--add-port", f"{port}/tcp", ])
    #subprocess.run(["firewall-cmd", "--reload"])

def close_firewalld_port(port):
    """Закрывает порт в firewalld."""
    print(f" 🔒  Закрытие порта {port} через firewalld...\n")
    subprocess.run(["firewall-cmd", "--remove-port", f"{port}/tcp", ])
    #subprocess.run(["firewall-cmd", "--reload"])
