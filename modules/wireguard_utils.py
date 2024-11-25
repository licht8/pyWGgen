#!/usr/bin/env python3
# modules/wireguard_utils.py
# Модуль для управления WireGuard

import os
import subprocess

WIREGUARD_BINARY = "/usr/bin/wg"
WIREGUARD_INSTALL_SCRIPT = "wireguard-install.sh"

def check_wireguard_installed():
    """Проверка, установлен ли WireGuard."""
    return os.path.isfile(WIREGUARD_BINARY)

def install_wireguard():
    """Установка WireGuard."""
    if os.path.isfile(WIREGUARD_INSTALL_SCRIPT):
        print("  🔧  Установка WireGuard...")
        subprocess.run(["bash", WIREGUARD_INSTALL_SCRIPT])
    else:
        print(f"  ❌  Скрипт {WIREGUARD_INSTALL_SCRIPT} не найден. Положите его в текущую директорию.")

def remove_wireguard():
    """Удаление WireGuard."""
    print("  ❌  Удаление WireGuard...")
    subprocess.run(["yum", "remove", "wireguard", "-y"], stderr=subprocess.DEVNULL) or \
    subprocess.run(["apt", "remove", "wireguard", "-y"], stderr=subprocess.DEVNULL)
