#!/usr/bin/env python3
# modules/install.py
# ===========================================
# Установщик WireGuard с креативным интерфейсом
# ===========================================
# Этот скрипт автоматически устанавливает WireGuard,
# настраивает сервер и создает начального пользователя.
# ===========================================

import time
from modules.firewall_utils import get_external_ip
from ai_diagnostics.ai_diagnostics import display_message_slowly
from settings import PRINT_SPEED, LINE_DELAY


def display_message(message, print_speed=None):
    """Отображает сообщение с имитацией печати."""
    display_message_slowly(f"{message}", print_speed=print_speed)

def main():
    local_print_speed = PRINT_SPEED  # Локальная скорость для изменения

    display_message(f"    ------------------------------------------", print_speed=local_print_speed)
    display_message(f"    ⚠️  WireGuard is already installed!", print_speed=local_print_speed)
    
    # Ожидание ответа пользователя
    reinstall = input(f"    ⚠️   Reinstall WireGuard? (yes/no): ").strip().lower()
    if reinstall != "yes":
        display_message(f"    Installation aborted. Exiting...", print_speed=local_print_speed)
        return
    
    display_message(f"    ------------------------------------------", print_speed=local_print_speed)
    display_message(f"    🍀 Installing WireGuard...", print_speed=local_print_speed)
    time.sleep(1)  # Эмуляция установки
    display_message(f"    ✅ WireGuard installed successfully!", print_speed=local_print_speed)
    
    display_message(f"    ------------------------------------------", print_speed=local_print_speed)
    display_message(f"    === 🛠️  WireGuard Installation ===", print_speed=local_print_speed)
    display_message(f"    Let's set up your WireGuard server!", print_speed=local_print_speed)
    display_message(f"    ------------------------------------------", print_speed=local_print_speed)
    
    external_ip = get_external_ip()
    display_message(f"    - 🌐 Detected external IP: {external_ip}", print_speed=local_print_speed)
    
    # Ожидание ввода данных от пользователя
    server_ip = input(f" 🌍 Enter server IP [auto-detect]: ").strip() or external_ip
    server_port = input(f" 🔒 Enter WireGuard port [51820]: ").strip() or "51820"
    subnet = input(f" 📡 Enter subnet for clients [10.66.66.0/24]: ").strip() or "10.66.66.0/24"
    dns_servers = input(f" 🧙‍♂️ Enter DNS servers [8.8.8.8, 8.8.4.4]: ").strip() or "8.8.8.8, 8.8.4.4"

    display_message(f"    🔧 Configuring WireGuard server...", print_speed=local_print_speed)
    time.sleep(1)  # Эмуляция настройки
    display_message(f"    ✅ Server configuration saved!", print_speed=local_print_speed)

    display_message(f"    🌱 Creating the initial user (SetupUser)...", print_speed=local_print_speed)
    time.sleep(1)  # Эмуляция создания пользователя

    # Логи с ровными колонками
    log_messages = [
        "2024-12-03 13:36:08,700 - INFO     ℹ️  Инициализация директорий.",
        "2024-12-03 13:36:08,701 - INFO     ℹ️  Загрузка параметров сервера.",
        "2024-12-03 13:36:08,701 - ERROR    ℹ️  Ошибка выполнения: File contains no section headers."
    ]
    for log in log_messages:
        display_message(log, print_speed=local_print_speed)
    
    display_message(f"    ✅ Initial user created successfully!", print_speed=local_print_speed)
    display_message(f"    🚀 Starting WireGuard...", print_speed=local_print_speed)
    time.sleep(1)  # Эмуляция запуска
    display_message(f"    ✅ WireGuard started successfully!", print_speed=local_print_speed)
    display_message(f"    🎉 WireGuard installation complete!", print_speed=local_print_speed)

if __name__ == "__main__":
    main()

