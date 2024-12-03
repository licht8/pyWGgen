#!/usr/bin/env python3
# wg_qr_generator/install.py
# ===========================================
# Скрипт для установки и настройки WireGuard
# ===========================================
# Назначение:
# - Установка WireGuard
# - Настройка сервера WireGuard
# - Создание первого пользователя через main.py
# - Настройка фаервола
#
# Использование:
# - Запустите скрипт из корня проекта wg_qr_generator:
#   $ python3 install.py
#
# Примечания:
# - Скрипт использует настройки из `settings.py`.
# - Все действия логируются в файл, указанный в `LOG_FILE_PATH`.
# ===========================================

import os
import shutil
import subprocess
import platform
import json
import time
from pathlib import Path
from settings import (
    SERVER_CONFIG_FILE,
    PARAMS_FILE,
    WG_CONFIG_DIR,
    QR_CODE_DIR,
    LOG_FILE_PATH,
    LOG_LEVEL,
    WIREGUARD_PORT,
    PRINT_SPEED,
    LINE_DELAY,
    DEFAULT_TRIAL_DAYS,
)
from ai_diagnostics.ai_diagnostics import display_message_slowly
import logging

# Настройка логгера
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=getattr(logging, LOG_LEVEL, "INFO"),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def display_message_with_spacing(message, print_speed=None):
    """Печатает сообщение с отступами от левой границы и между блоками."""
    print()  # Отступ перед блоком
    display_message_slowly(message, print_speed)
    print()  # Отступ после блока

def detect_package_manager():
    """Определяет пакетный менеджер для текущей системы."""
    distro = platform.system()
    if distro == "Linux":
        with open("/etc/os-release", "r") as f:
            os_release = f.read()
            if "Ubuntu" in os_release:
                return "apt"
            elif "CentOS" in os_release or "Stream" in os_release:
                return "dnf"
    display_message_with_spacing("❌ Unsupported OS or distribution. Exiting.", PRINT_SPEED)
    logger.error("Unsupported OS or distribution.")
    exit(1)

def install_wireguard():
    """Устанавливает WireGuard."""
    package_manager = detect_package_manager()
    try:
        display_message_with_spacing("🍀 Installing WireGuard...", PRINT_SPEED)
        if package_manager == "apt":
            subprocess.run(["apt", "update"], check=True)
            subprocess.run(["apt", "install", "-y", "wireguard", "wireguard-tools"], check=True)
        elif package_manager == "dnf":
            subprocess.run(["dnf", "install", "-y", "epel-release"], check=True)
            subprocess.run(["dnf", "install", "-y", "wireguard-tools"], check=True)
        display_message_with_spacing("✅ WireGuard installed successfully!", PRINT_SPEED)
        logger.info("WireGuard installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install WireGuard: {e}")
        display_message_with_spacing("❌ Failed to install WireGuard. Check logs for details.", PRINT_SPEED)
        exit(1)

def collect_user_input():
    """Собирает ввод от пользователя с креативными подсказками."""
    display_message_with_spacing("=== 🛠️  WireGuard Installation ===", PRINT_SPEED)
    display_message_with_spacing("Let's set up your WireGuard server!", PRINT_SPEED)
    
    server_ip = input(" 🌍 Enter server IP [auto-detect]: ").strip() or "auto-detect"
    port = input(f" 🔒 Enter WireGuard port [{WIREGUARD_PORT}]: ").strip() or WIREGUARD_PORT
    subnet = input(" 📡 Enter subnet for clients [10.66.66.0/24]: ").strip() or "10.66.66.0/24"
    dns = input(" 🧙‍♂️ Enter DNS servers [8.8.8.8, 8.8.4.4]: ").strip() or "8.8.8.8, 8.8.4.4"

    return {
        "server_ip": server_ip,
        "port": port,
        "subnet": subnet,
        "dns": dns,
    }

def configure_server(server_ip, port, subnet, dns):
    """Создаёт серверную конфигурацию."""
    try:
        display_message_with_spacing("🔧 Configuring WireGuard server...", PRINT_SPEED)
        private_key = subprocess.check_output(["wg", "genkey"]).strip()
        public_key = subprocess.check_output(["echo", private_key, "|", "wg", "pubkey"]).strip()

        with open(SERVER_CONFIG_FILE, "w") as config:
            config.write(f"""
[Interface]
PrivateKey = {private_key.decode()}
Address = {subnet.split('/')[0]}
ListenPort = {port}
SaveConfig = true

PostUp = firewall-cmd --zone=public --add-interface=%i
PostUp = firewall-cmd --add-port={port}/udp
PostUp = firewall-cmd --add-rich-rule="rule family=ipv4 source address={subnet} masquerade"
PostDown = firewall-cmd --zone=public --remove-interface=%i
PostDown = firewall-cmd --remove-port={port}/udp
PostDown = firewall-cmd --remove-rich-rule="rule family=ipv4 source address={subnet} masquerade"
""")

        # Save parameters
        with open(PARAMS_FILE, "w") as params:
            params.write(f"""
SERVER_PUB_IP={server_ip}
SERVER_PORT={port}
SERVER_PUB_KEY={public_key.decode()}
SERVER_PRIV_KEY={private_key.decode()}
SERVER_SUBNET={subnet}
CLIENT_DNS={dns}
""")
        display_message_with_spacing("✅ Server configuration saved!", PRINT_SPEED)
        logger.info("Server configuration saved.")
    except Exception as e:
        logger.error(f"Failed to configure server: {e}")
        display_message_with_spacing("❌ Failed to configure server. Check logs for details.", PRINT_SPEED)
        exit(1)

def create_initial_user():
    """Создаёт первого пользователя через main.py."""
    try:
        display_message_with_spacing("🌱 Creating the initial user (SetupUser)...", PRINT_SPEED)
        subprocess.run(["python3", "main.py", "SetupUser"], check=True)
        display_message_with_spacing("✅ Initial user created successfully!", PRINT_SPEED)
        logger.info("Initial user created successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create initial user: {e}")
        display_message_with_spacing("❌ Failed to create initial user. Check logs for details.", PRINT_SPEED)

def start_wireguard():
    """Запускает WireGuard."""
    try:
        display_message_with_spacing("🚀 Starting WireGuard...", PRINT_SPEED)
        subprocess.run(["systemctl", "start", "wg-quick@wg0"], check=True)
        display_message_with_spacing("✅ WireGuard started successfully!", PRINT_SPEED)
        logger.info("WireGuard started successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start WireGuard: {e}")
        display_message_with_spacing("❌ Failed to start WireGuard. Check logs for details.", PRINT_SPEED)

def main():
    """Основная функция установки."""
    if shutil.which("wg"):
        display_message_with_spacing("⚠️ WireGuard is already installed. Do you want to reinstall it? (yes/no): ", PRINT_SPEED, end="")
        if input().strip().lower() != "yes":
            display_message_with_spacing("❌ Installation cancelled.", PRINT_SPEED)
            return

    # Установка WireGuard
    install_wireguard()

    # Сбор параметров
    params = collect_user_input()

    # Настройка сервера
    configure_server(**params)

    # Создание первого пользователя
    create_initial_user()

    # Запуск WireGuard
    start_wireguard()

    display_message_with_spacing("🎉 WireGuard installation complete!", PRINT_SPEED)

if __name__ == "__main__":
    main()
