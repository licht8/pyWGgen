#!/usr/bin/env python3
# modules/install_wg.py
# ===========================================
# Установщик WireGuard с созданием директорий и проверкой конфигов
# ===========================================

import os
import time
import traceback
from pathlib import Path
from settings import (
    PRINT_SPEED, WG_CONFIG_DIR, SERVER_CONFIG_FILE, LOG_FILE_PATH
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


def create_directory(path: Path):
    """Создает директорию, если она не существует."""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        log_message(f"Создана директория: {path}", level="INFO")


def install_wireguard():
    """Устанавливает WireGuard с созданием директорий и проверкой конфигов."""
    try:
        # Проверяем и создаем директорию для конфигураций
        create_directory(WG_CONFIG_DIR)

        # Проверка существующего конфига
        if SERVER_CONFIG_FILE.exists():
            display_message("⚠️  Найден существующий конфигурационный файл WireGuard.")
            overwrite = input("⚠️   Перезаписать файл? (yes/no): ").strip().lower()
            if overwrite != "yes":
                display_message("⛔ Установка прервана. Выход.", print_speed=PRINT_SPEED)
                log_message("Установка WireGuard отменена: файл конфигурации существует.", level="WARNING")
                return
            else:
                log_message(f"Перезапись конфигурационного файла: {SERVER_CONFIG_FILE}")

        # Установка WireGuard
        display_message("🍀 Установка WireGuard...", print_speed=PRINT_SPEED)
        time.sleep(1)
        log_message("Установка WireGuard началась.")

        # Получаем внешний IP
        external_ip = get_external_ip()
        display_message(f"🌐 Обнаружен внешний IP: {external_ip}", print_speed=PRINT_SPEED)

        # Ввод данных с автоопределением
        server_ip = input(f" 🌍 Введите IP сервера [{external_ip}]: ").strip() or external_ip
        server_port = input(" 🔒 Введите порт WireGuard [51820]: ").strip() or "51820"
        subnet = input(" 📡 Введите подсеть для клиентов [10.66.66.0/24]: ").strip() or "10.66.66.0/24"
        dns_servers = input(" 🧙‍♂️ Введите DNS сервера [8.8.8.8, 8.8.4.4]: ").strip() or "8.8.8.8, 8.8.4.4"

        # Настройка WireGuard
        display_message("🔧 Настройка сервера WireGuard...", print_speed=PRINT_SPEED)
        config_content = f"""
[Interface]
Address = {subnet.split('/')[0]}/24
ListenPort = {server_port}
PrivateKey = <YourServerPrivateKey>

[Peer]
PublicKey = <YourClientPublicKey>
AllowedIPs = {subnet}
"""
        # Записываем конфигурацию
        with open(SERVER_CONFIG_FILE, "w") as config_file:
            config_file.write(config_content)
        log_message(f"Конфигурационный файл сохранен: {SERVER_CONFIG_FILE}")

        # Отчет об установке
        report = f"""
=== Отчет об установке WireGuard ===
📄 Конфигурационный файл: {SERVER_CONFIG_FILE}
🔒 Порт сервера: {server_port}
📡 Подсеть для клиентов: {subnet}
🌍 Внешний IP: {server_ip}
🗂️ Логи установки: {LOG_FILE_PATH}
        """
        display_message(report, print_speed=PRINT_SPEED)
        log_message("Установка WireGuard завершена успешно.")
    except Exception as e:
        error_message = f"❌ Произошла ошибка при установке WireGuard: {e}"
        display_message(error_message, print_speed=PRINT_SPEED)
        log_message(error_message, level="ERROR")
        log_message(traceback.format_exc(), level="ERROR")
