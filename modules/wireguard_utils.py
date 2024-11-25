#!/usr/bin/env python3
# modules/wireguard_utils.py
# Функции для работы с WireGuard

import os
import subprocess

WIREGUARD_BINARY = "/usr/bin/wg"

def check_wireguard_installed():
    """Проверяет, установлен ли WireGuard."""
    return os.path.isfile(WIREGUARD_BINARY)

def install_wireguard():
    """Устанавливает WireGuard."""
    print("🔧 Установка WireGuard...")
    subprocess.run(["apt-get", "install", "-y", "wireguard"])

def remove_wireguard():
    """Удаляет WireGuard."""
    print("❌ Удаление WireGuard...")
    subprocess.run(["apt-get", "remove", "-y", "wireguard"])
