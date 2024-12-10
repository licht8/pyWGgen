#!/usr/bin/env python3
# modules/install_wg.py
# ===========================================
# Установщик WireGuard с расширенной отладкой и проверками
# Версия 1.2
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


def install_wireguard_package():
    """Устанавливает WireGuard через пакетный менеджер."""
    try:
        display_message("📦 Установка пакетов WireGuard...", print_speed=PRINT_SPEED)
        if shutil.which("apt"):
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "wireguard"], check=True)
        elif shutil.which("yum"):
            subprocess.run(["sudo", "yum", "install", "-y", "epel-release"], check=True)
            subprocess.run(["sudo", "yum", "install", "-y", "wireguard-tools"], check=True)
        else:
            raise EnvironmentError("Не удалось определить пакетный менеджер для установки WireGuard.")
        verify_wireguard_installation()
        log_message("WireGuard установлен успешно.", level="INFO")
    except subprocess.CalledProcessError as e:
        error_message = f"Ошибка при установке WireGuard: {e}"
        display_message(f"❌ {error_message}", print_speed=PRINT_SPEED)
        log_message(error_message, level="ERROR")
        raise


def verify_wireguard_installation():
    """Проверяет, установлен ли WireGuard корректно."""
    wg_path = shutil.which("wg")
    if not wg_path:
        raise FileNotFoundError("Команда 'wg' не найдена после установки.")
    try:
        version_output = subprocess.check_output([wg_path, "--version"], stderr=subprocess.STDOUT).decode().strip()
        wg_show_output = subprocess.run(
            [wg_path, "show"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        log_message(f"WireGuard версия: {version_output}", level="INFO")
        if wg_show_output.returncode != 0:
            log_message(f"Ошибка команды 'wg show': {wg_show_output.stderr.strip()}", level="WARNING")
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


def install_wireguard():
    """Устанавливает WireGuard с расширенной проверкой и отладкой."""
    try:
        # Проверяем и создаем необходимые директории
        create_directory(WG_CONFIG_DIR)
        create_directory(QR_CODE_DIR)

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
        install_wireguard_package()
        verify_wireguard_installation()
        verify_firewalld()
        verify_masquerade()

        # Продолжение настройки (генерация ключей, конфигурация сервера и клиента)
        # (Содержимое вашего оригинального метода install_wireguard продолжает использоваться здесь)

    except Exception as e:
        error_message = f"❌ Установка WireGuard завершилась с ошибкой: {e}"
        display_message(error_message, print_speed=PRINT_SPEED)
        log_message(error_message, level="ERROR")
        log_message(traceback.format_exc(), level="ERROR")
