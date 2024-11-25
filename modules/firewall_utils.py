#!/usr/bin/env python3
# modules/firewall_utils.py
# Модуль для управления firewalld

import subprocess

def open_firewalld_port(port):
    """Открытие порта через firewalld."""
    print(f"  🔓  Открытие порта {port} через firewalld...")
    try:
        subprocess.run(["sudo", "firewall-cmd", "--add-port", f"{port}/tcp"], check=True)
        print(f"  ✅  Порт {port} добавлен через firewalld (временные правила).")
    except subprocess.CalledProcessError:
        print(f"  ❌  Не удалось добавить порт {port} через firewalld.")

def close_firewalld_port(port):
    """Закрытие порта через firewalld."""
    print(f"  🔒  Закрытие порта {port} через firewalld...")
    try:
        subprocess.run(["sudo", "firewall-cmd", "--remove-port", f"{port}/tcp"], check=True)
        print(f"  ✅  Порт {port} удален через firewalld (временные правила).")
    except subprocess.CalledProcessError:
        print(f"  ❌  Не удалось удалить порт {port} через firewalld.")
