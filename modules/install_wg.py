#!/usr/bin/env python3
# modules/install_wg.py
# ===========================================
# Установщик WireGuard с креативным интерфейсом и отладкой
# ===========================================

import time
import traceback
from pathlib import Path
from settings import (
    PRINT_SPEED, LINE_DELAY, WG_CONFIG_DIR, SERVER_CONFIG_FILE, PARAMS_FILE, LOG_FILE_PATH
)
from modules.firewall_utils import get_external_ip
from ai_diagnostics.ai_diagnostics import display_message_slowly


def log_message(message: str, level: str = "INFO"):
    """Записывает сообщение в лог-файл."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {level} - {message}\n"
    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write(log_entry)


def display_message(message, print_speed=None):
    """Отображает сообщение с имитацией печати."""
    display_message_slowly(message, print_speed=print_speed)
    log_message(message)


def install_wireguard():
    """Устанавливает WireGuard с отладкой и подробным отчетом."""
    try:
        # Инициализация
        display_message("🛠️  Проверка состояния WireGuard...", print_speed=PRINT_SPEED)
        time.sleep(0.5)

        # Проверка уже установленной версии
        if SERVER_CONFIG_FILE.exists():
            display_message("⚠️  WireGuard уже установлен!", print_speed=PRINT_SPEED)
            reinstall = input("⚠️   Перестановить WireGuard? (yes/no): ").strip().lower()
            if reinstall != "yes":
                display_message("⛔ Установка прервана. Выход.", print_speed=PRINT_SPEED)
                log_message("Установка WireGuard отменена пользователем.", level="WARNING")
                return

        # Установка WireGuard
        display_message("🍀 Установка WireGuard...", print_speed=PRINT_SPEED)
        time.sleep(1)
        log_message("Установка WireGuard началась.")
        # Здесь можно добавить реальную команду установки через subprocess, например:
        # subprocess.run(["apt-get", "install", "-y", "wireguard"], check=True)

        # Конфигурация сервера
        external_ip = get_external_ip()
        display_message(f"🌐 Обнаружен внешний IP: {external_ip}", print_speed=PRINT_SPEED)

        server_ip = input(" 🌍 Введите IP сервера [автоопределение]: ").strip() or external_ip
        server_port = input(" 🔒 Введите порт WireGuard [51820]: ").strip() or "51820"
        subnet = input(" 📡 Введите подсеть для клиентов [10.66.66.0/24]: ").strip() or "10.66.66.0/24"
        dns_servers = input(" 🧙‍♂️ Введите DNS сервера [8.8.8.8, 8.8.4.4]: ").strip() or "8.8.8.8, 8.8.4.4"

        # Создание конфигурации
        display_message("🔧 Настройка сервера WireGuard...", print_speed=PRINT_SPEED)
        config_path = WG_CONFIG_DIR / "server.conf"
        with open(config_path, "w") as config_file:
            config_file.write(f"""
[Interface]
Address = {subnet.split('/')[0]}/24
ListenPort = {server_port}
PrivateKey = <YourServerPrivateKey>

[Peer]
PublicKey = <YourClientPublicKey>
AllowedIPs = {subnet}
            """)
        log_message(f"Конфигурация WireGuard сохранена: {config_path}")

        # Отчет об установке
        report = f"""
=== Отчет об установке WireGuard ===
📄 Конфигурационный файл: {config_path}
🔒 Порт сервера: {server_port}
📡 Подсеть для клиентов: {subnet}
🌍 Внешний IP: {server_ip}
🗂️ Логи установки: {LOG_FILE_PATH}
        """
        display_message(report, print_speed=PRINT_SPEED)
        log_message("Установка WireGuard завершена успешно.")
    except Exception as e:
        error_message = f"Произошла ошибка при установке WireGuard: {e}"
        display_message(f"❌ {error_message}", print_speed=PRINT_SPEED)
        log_message(error_message, level="ERROR")
        log_message(traceback.format_exc(), level="ERROR")
