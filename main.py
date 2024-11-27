#!/usr/bin/env python3
# main.py
## Основной скрипт для создания пользователей WireGuard

import sys
import os
import json
from datetime import datetime, timedelta
import settings
from modules.config import load_params
from modules.keygen import generate_private_key, generate_public_key, generate_preshared_key
from modules.ip_management import generate_ip
from modules.config_writer import add_user_to_server_config
from modules.qr_generator import generate_qr_code
from modules.directory_setup import setup_directories
from modules.client_config import create_client_config
import subprocess
import logging

# Настройка логгера
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)-8s %(message)s",
    handlers=[logging.StreamHandler()]
)

DEBUG_EMOJI = "🐛"
INFO_EMOJI = "ℹ️"
WARNING_EMOJI = "⚠️"
ERROR_EMOJI = "❌"

class EmojiLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        if kwargs.get('level', logging.INFO) == logging.DEBUG:
            msg = f"{DEBUG_EMOJI}  {msg}"
        elif kwargs.get('level', logging.INFO) == logging.INFO:
            msg = f"{INFO_EMOJI}  {msg}"
        elif kwargs.get('level', logging.INFO) == logging.WARNING:
            msg = f"{WARNING_EMOJI}  {msg}"
        elif kwargs.get('level', logging.INFO) == logging.ERROR:
            msg = f"{ERROR_EMOJI}  {msg}"
        return msg, kwargs

logger = EmojiLoggerAdapter(logging.getLogger(__name__), {})

def load_existing_users():
    """
    Загружает список существующих пользователей из базы данных.
    """
    user_records_path = os.path.join("user", "data", "user_records.json")
    if os.path.exists(user_records_path):
        with open(user_records_path, "r", encoding="utf-8") as file:
            try:
                user_data = json.load(file)
                return {user.lower(): user_data[user] for user in user_data}  # Нормализуем имена
            except json.JSONDecodeError:
                logger.warning("Ошибка чтения базы данных пользователей.")
                return {}
    return {}

def is_user_in_server_config(nickname, config_file):
    """
    Проверяет наличие пользователя в конфигурации сервера.
    """
    nickname_lower = nickname.lower()
    try:
        with open(config_file, "r") as file:
            for line in file:
                if nickname_lower in line.lower():
                    return True
    except FileNotFoundError:
        logger.warning(f"Файл конфигурации {config_file} не найден.")
    return False

def restart_wireguard(interface="wg0"):
    """
    Перезапускает WireGuard.
    """
    try:
        subprocess.run(["sudo", "systemctl", "restart", f"wg-quick@{interface}"], check=True)
        logger.info(f"WireGuard {interface} успешно перезапущен.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка перезапуска WireGuard: {e}")

def generate_config(nickname, params, config_file, email="N/A", telegram_id="N/A"):
    """
    Генерация конфигурации пользователя и QR-кода.
    """
    logger.info(f"Начало генерации конфигурации для пользователя: {nickname}")
    server_public_key = params['SERVER_PUB_KEY']
    endpoint = f"{params['SERVER_PUB_IP']}:{params['SERVER_PORT']}"
    dns_servers = f"{params['CLIENT_DNS_1']},{params['CLIENT_DNS_2']}"

    private_key = generate_private_key()
    logger.debug("Приватный ключ сгенерирован.")
    public_key = generate_public_key(private_key)
    logger.debug("Публичный ключ сгенерирован.")
    preshared_key = generate_preshared_key()
    logger.debug("Пресекретный ключ сгенерирован.")

    # Генерация IP-адреса
    address, new_ipv4 = generate_ip(config_file)
    logger.info(f"IP-адрес сгенерирован: {address}")

    # Генерация конфигурации клиента
    client_config = create_client_config(
        private_key=private_key,
        address=address,
        dns_servers=dns_servers,
        server_public_key=server_public_key,
        preshared_key=preshared_key,
        endpoint=endpoint
    )
    logger.debug("Конфигурация клиента создана.")

    config_path = os.path.join(settings.WG_CONFIG_DIR, f"{nickname}.conf")
    qr_path = os.path.join(settings.QR_CODE_DIR, f"{nickname}.png")

    # Сохраняем конфигурацию
    os.makedirs(settings.WG_CONFIG_DIR, exist_ok=True)
    with open(config_path, "w") as file:
        file.write(client_config)
    logger.info(f"Конфигурация клиента сохранена в {config_path}")

    # Генерация QR-кода
    generate_qr_code(client_config, qr_path)
    logger.info(f"QR-код сохранён в {qr_path}")

    # Добавление пользователя в конфигурацию сервера
    add_user_to_server_config(config_file, nickname, public_key.decode('utf-8'), preshared_key.decode('utf-8'), address)
    logger.info("Пользователь добавлен в конфигурацию сервера.")

    # Добавление записи пользователя
    try:
        add_user_record(
            nickname,
            trial_days=settings.DEFAULT_TRIAL_DAYS,
            address=address,
            public_key=public_key.decode('utf-8'),
            preshared_key=preshared_key.decode('utf-8'),
            qr_code_path=qr_path,  # Передача переменной qr_path
            email=email,
            telegram_id=telegram_id
        )
    except Exception as e:
        logger.error(f"Ошибка добавления записи пользователя: {e}")

    # Перезапуск WireGuard
    restart_wireguard(params['SERVER_WG_NIC'])

    return config_path, qr_path

def add_user_record(nickname, trial_days, address, public_key, preshared_key, qr_code_path, email, telegram_id):
    """
    Добавляет запись о пользователе с расширенными данными.
    """
    logger.info(f"Добавление записи пользователя {nickname} в базу данных.")
    user_records_path = os.path.join("user", "data", "user_records.json")
    expiry_date = datetime.now() + timedelta(days=trial_days)

    # Загружаем существующие записи
    if os.path.exists(user_records_path):
        with open(user_records_path, "r", encoding="utf-8") as file:
            try:
                user_data = json.load(file)
            except json.JSONDecodeError:
                logger.warning("Ошибка чтения базы данных пользователей, будет создана новая.")
                user_data = {}
    else:
        user_data = {}

    # Проверяем, чтобы не было дубликатов
    if nickname in user_data:
        logger.error(f"Пользователь с именем '{nickname}' уже существует в базе данных.")
        raise ValueError(f"Пользователь с именем '{nickname}' уже существует.")

    # Добавляем новую запись
    user_data[nickname] = {
        "username": nickname,
        "created_at": datetime.now().isoformat(),
        "expires_at": expiry_date.isoformat(),
        "allowed_ips": address,
        "public_key": public_key,
        "preshared_key": preshared_key,
        "endpoint": "N/A",  # будет обновляться позже
        "last_handshake": "N/A",  # будет обновляться позже
        "uploaded": "N/A",  # будет обновляться позже
        "downloaded": "N/A",  # будет обновляться позже
        "qr_code_path": qr_code_path,  # Используем переданную переменную qr_code_path
        "email": email,
        "telegram_id": telegram_id,
        "status": "inactive"
    }

    # Сохраняем обновленные данные
    os.makedirs(os.path.dirname(user_records_path), exist_ok=True)
    with open(user_records_path, "w", encoding="utf-8") as file:
        json.dump(user_data, file, indent=4)
    logger.info(f"Данные пользователя {nickname} успешно добавлены в {user_records_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Недостаточно аргументов. Использование: python3 main.py <nickname> [email] [telegram_id]")
        sys.exit(1)

    nickname = sys.argv[1]
    email = sys.argv[2] if len(sys.argv) > 2 else "N/A"
    telegram_id = sys.argv[3] if len(sys.argv) > 3 else "N/A"
    params_file = settings.PARAMS_FILE

    # Проверка существующего пользователя
    existing_users = load_existing_users()
    if nickname.lower() in existing_users:
        logger.error(f"Пользователь с именем '{nickname}' уже существует в базе данных.")
        sys.exit(1)

    if is_user_in_server_config(nickname, settings.SERVER_CONFIG_FILE):
        logger.error(f"Пользователь с именем '{nickname}' уже существует в конфигурации сервера.")
        sys.exit(1)

    try:
        logger.info("Инициализация директорий.")
        setup_directories()

        logger.info("Загрузка параметров сервера.")
        params = load_params(params_file)

        logger.info("Генерация конфигурации пользователя.")
        config_file = settings.SERVER_CONFIG_FILE
        config_path, qr_path = generate_config(nickname, params, config_file, email, telegram_id)

        logger.info(f"✅ Конфигурация сохранена в {config_path}")
        logger.info(f"✅ QR-код сохранён в {qr_path}")
    except Exception as e:
        logger.error(f"Ошибка выполнения: {e}")
