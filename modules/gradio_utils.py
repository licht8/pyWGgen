#!/usr/bin/env python3
# gradio_utils.py
# Утилиты для запуска Gradio интерфейса

import os
import subprocess
import socket
from gradio_admin.main_interface import admin_interface

FIREWALLD_ZONE = "public"
GRADIO_PORT = 7860

def is_port_in_use(port):
    """Проверяет, занят ли порт."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def open_firewalld_port(port):
    """Открывает порт через firewalld."""
    try:
        subprocess.run(["firewall-cmd", "--zone", FIREWALLD_ZONE, "--add-port", f"{port}/tcp"], check=True)
        subprocess.run(["firewall-cmd", "--zone", FIREWALLD_ZONE, "--add-port", f"{port}/udp"], check=True)
        print(f"✅ Открыт порт {port} через firewalld.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при открытии порта {port}: {e}")

def close_firewalld_port(port):
    """Закрывает порт через firewalld."""
    try:
        subprocess.run(["firewall-cmd", "--zone", FIREWALLD_ZONE, "--remove-port", f"{port}/tcp"], check=True)
        subprocess.run(["firewall-cmd", "--zone", FIREWALLD_ZONE, "--remove-port", f"{port}/udp"], check=True)
        print(f"✅ Закрыт порт {port} через firewalld.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при закрытии порта {port}: {e}")

def run_gradio_admin_interface():
    """Запускает Gradio интерфейс."""
    if is_port_in_use(GRADIO_PORT):
        print(f"❌ Порт {GRADIO_PORT} уже используется. Проверьте или выберите другой порт.")
        return

    # Открываем порт через firewalld
    open_firewalld_port(GRADIO_PORT)

    try:
        print("🌐 Запуск Gradio интерфейса...")
        admin_interface.launch(server_name="0.0.0.0", server_port=GRADIO_PORT, share=True)
    finally:
        # Закрываем порт после завершения работы
        close_firewalld_port(GRADIO_PORT)
