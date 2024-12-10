#!/usr/bin/env python3
# modules/install_wg.py
# ===========================================
# Установщик WireGuard с расширенной отладкой и проверками
# Версия 1.5
# ===========================================

import os
import time
import subprocess
import traceback
from pathlib import Path
import shutil
import base64
from settings import (
    PRINT_SPEED,
    WG_CONFIG_DIR,
    QR_CODE_DIR,
    SERVER_CONFIG_FILE,
    LOG_FILE_PATH,
    LOG_LEVEL,
    DEFAULT_TRIAL_DAYS,
)
from modules.firewall_utils import get_external_ip
from ai_diagnostics.ai_diagnostics import display_message_slowly
import qrcode


def log_message(message: str, level: str = "INFO"):
    """Записывает сообщение в лог-файл с учетом уровня логирования."""
    if LOG_LEVEL == "DEBUG" or level != "DEBUG":
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
    try:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            log_message(f"Создана директория: {path}", level="DEBUG")
    except Exception as e:
        error_message = f"Ошибка создания директории {path}: {e}"
        log_message(error_message, level="ERROR")
        raise RuntimeError(error_message)


def generate_qr_code(config: str, file_path: Path):
    """Генерирует QR-код для конфигурации."""
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(config)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")
        img.save(file_path)
        log_message(f"QR-код сохранен: {file_path}", level="INFO")
    except Exception as e:
        error_message = f"Ошибка генерации QR-кода: {e}"
        log_message(error_message, level="ERROR")
        raise RuntimeError(error_message)


def install_wireguard_package():
    """Устанавливает WireGuard через пакетный менеджер."""
    try:
        display_message("📦 Установка пакетов WireGuard...", print_speed=PRINT_SPEED)
        if shutil.which("apt"):
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "wireguard"], check=True)
        elif shutil.which("yum"):
            subprocess.run(["sudo", "yum", "install", "-y", "epel-release", "elrepo-release"], check=True)
            subprocess.run(["sudo", "yum", "install", "-y", "wireguard-tools", "kmod-wireguard"], check=True)
        else:
            raise EnvironmentError("Не удалось определить пакетный менеджер для установки WireGuard.")
        log_message("WireGuard установлен успешно.", level="INFO")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Ошибка установки WireGuard: {e}")


def verify_wireguard_installation():
    """Проверяет, установлен ли WireGuard корректно."""
    wg_path = shutil.which("wg")
    if not wg_path:
        raise FileNotFoundError("Команда 'wg' не найдена после установки.")
    try:
        version_output = subprocess.check_output([wg_path, "--version"], stderr=subprocess.STDOUT).decode().strip()
        log_message(f"WireGuard версия: {version_output}", level="INFO")
        display_message(f"✅ WireGuard успешно установлен: {version_output}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"WireGuard установлен, но команда 'wg show' вернула ошибку: {e}")


def verify_firewalld():
    """Проверяет и включает firewalld."""
    try:
        firewall_state = subprocess.run(
            ["firewall-cmd", "--state"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if "running" not in firewall_state.stdout:
            display_message("⚠️  Firewalld не запущен. Попытка запуска...", print_speed=PRINT_SPEED)
            subprocess.run(["sudo", "systemctl", "start", "firewalld"], check=True)
            log_message("Firewalld успешно запущен.", level="INFO")
    except subprocess.CalledProcessError as e:
        log_message(f"Ошибка запуска firewalld: {e}", level="ERROR")
        display_message(f"❌ Ошибка запуска firewalld: {e}")


def verify_masquerade():
    """Проверяет и настраивает правила маскарадинга."""
    try:
        masquerade_check = subprocess.run(
            ["firewall-cmd", "--query-masquerade"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if "yes" not in masquerade_check.stdout:
            display_message("🔧 Включение маскарадинга...", print_speed=PRINT_SPEED)
            subprocess.run(["sudo", "firewall-cmd", "--add-masquerade"], check=True)
            subprocess.run(["sudo", "firewall-cmd", "--runtime-to-permanent"], check=True)
            log_message("Маскарадинг включен.", level="INFO")
    except subprocess.CalledProcessError as e:
        log_message(f"Ошибка настройки маскарадинга: {e}", level="ERROR")
        display_message(f"❌ Ошибка настройки маскарадинга: {e}")


def generate_keypair():
    """Генерирует приватный и публичный ключи."""
    wg_path = shutil.which("wg")
    if not wg_path:
        install_wireguard_package()
    try:
        private_key = subprocess.check_output([wg_path, "genkey"]).decode().strip()
        public_key = subprocess.check_output([wg_path, "pubkey"], input=private_key.encode()).decode().strip()
        return private_key, public_key
    except subprocess.SubprocessError as e:
        raise RuntimeError(f"Ошибка при генерации ключей: {e}")


def install_wireguard():
    """Устанавливает WireGuard с расширенной проверкой и отладкой."""
    try:
        create_directory(WG_CONFIG_DIR)
        create_directory(QR_CODE_DIR)

        if SERVER_CONFIG_FILE.exists():
            display_message("⚠️  Найден существующий конфигурационный файл WireGuard.")
            overwrite = input("⚠️   Перезаписать файл? (yes/no): ").strip().lower()
            if overwrite != "yes":
                display_message("⛔ Установка прервана. Выход.", print_speed=PRINT_SPEED)
                return

        install_wireguard_package()
        verify_wireguard_installation()
        verify_firewalld()
        verify_masquerade()

        server_private_key, server_public_key = generate_keypair()
        client_private_key, client_public_key = generate_keypair()
        preshared_key = base64.b64encode(os.urandom(32)).decode()

        external_ip = get_external_ip()
        server_ip = external_ip
        server_port = "51820"
        subnet = "10.66.66.1/24"
        ipv6_subnet = "fd42:42:42::1/64"
        dns_servers = "8.8.8.8, 8.8.4.4"

        server_config = f"""
[Interface]
Address = {subnet},{ipv6_subnet}
ListenPort = {server_port}
PrivateKey = {server_private_key}
PostUp = firewall-cmd --add-port {server_port}/udp && firewall-cmd --add-rich-rule='rule family=ipv4 source address=10.66.66.0/24 masquerade' && firewall-cmd --add-rich-rule='rule family=ipv6 source address=fd42:42:42::/64 masquerade'
PostDown = firewall-cmd --remove-port {server_port}/udp && firewall-cmd --remove-rich-rule='rule family=ipv4 source address=10.66.66.0/24 masquerade' && firewall-cmd --remove-rich-rule='rule family=ipv6 source address=fd42:42:42::/64 masquerade'

### Client SetupUser_HphD
[Peer]
PublicKey = {client_public_key}
PresharedKey = {preshared_key}
AllowedIPs = 10.66.66.2/32,fd42:42:42::2/128
        """

        with open(SERVER_CONFIG_FILE, "w") as config_file:
            config_file.write(server_config)

        client_config = f"""
[Interface]
PrivateKey = {client_private_key}
Address = 10.66.66.2/32,fd42:42:42::2/128
DNS = {dns_servers}

[Peer]
PublicKey = {server_public_key}
PresharedKey = {preshared_key}
Endpoint = {server_ip}:{server_port}
AllowedIPs = 0.0.0.0/0,::/0
        """

        qr_code_path = QR_CODE_DIR / "SetupUser_HphD.png"
        generate_qr_code(client_config, qr_code_path)

        display_message(f"✅ Установка завершена. QR-код сохранен: {qr_code_path}")
    except Exception as e:
        log_message(f"Ошибка: {e}", level="ERROR")


if __name__ == "__main__":
    install_wireguard()
