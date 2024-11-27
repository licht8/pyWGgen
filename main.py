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
from modules.main_registration_fields import create_user_record
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
WG_EMOJI = "🌐"
FIREWALL_EMOJI = "🛡️"

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
                logger.warning("Ошибка чтения базы данных пользователей, будет создана новая.")
                return {}
    return {}

def save_user_record(user_record):
    """
    Сохраняет информацию о пользователе в файл user_records.json.
    """
    user_records_path = os.path.join("user", "data", "user_records.json")
    os.makedirs(os.path.dirname(user_records_path), exist_ok=True)

    # Загружаем существующие записи
    if os.path.exists(user_records_path):
        with open(user_records_path, "r", encoding="utf-8") as file:
            try:
                user_data = json.load(file)
            except json.JSONDecodeError:
                logger.warning("Ошибка чтения базы данных пользователей. Создаём новый файл.")
                user_data = {}
    else:
        user_data = {}

    # Проверка на уникальность имени пользователя
    if user_record['username'].lower() in user_data:
        logger.error(f"Пользователь с именем '{user_record['username']}' уже существует в базе данных.")
        raise ValueError(f"Пользователь с именем '{user_record['username']}' уже существует.")

    # Добавляем новую запись
    user_data[user_record['username']] = user_record

    # Сохраняем данные в файл
    with open(user_records_path, "w", encoding="utf-8") as file:
        json.dump(user_data, file, indent=4)
    logger.info(f"Данные пользователя {user_record['username']} успешно добавлены в {user_records_path}")

def restart_wireguard(interface="wg0"):
    """
    Перезапускает WireGuard и показывает его статус.
    """
    try:
        subprocess.run(["sudo", "systemctl", "restart", f"wg-quick@{interface}"], check=True)
        logger.info(f"WireGuard {interface} успешно перезапущен.")

        # Получение статуса WireGuard
        wg_status = subprocess.check_output(["sudo", "systemctl", "status", f"wg-quick@{interface}"]).decode()
        for line in wg_status.splitlines():
            if "Active:" in line:
                logger.info(f"{WG_EMOJI}  {line.strip()}")

        # Вывод состояния firewall
        firewall_status = subprocess.check_output(["sudo", "firewall-cmd", "--list-ports"]).decode()
        for line in firewall_status.splitlines():
            logger.info(f"{FIREWALL_EMOJI}  {line.strip()}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка перезапуска WireGuard: {e}")

def generate_config(nickname, params, config_file, email="N/A", telegram_id="N/A"):
    """
    Генерация конфигурации пользователя и QR-кода.
    """
    logger.info(f"Начало генерации конфигурации для пользователя: {nickname}")
    
    # Проверяем наличие всех необходимых параметров
    required_keys = ['SERVER_PUB_KEY', 'SERVER_PUB_IP', 'SERVER_PORT', 'CLIENT_DNS_1', 'CLIENT_DNS_2', 'SERVER_SUBNET']
    for key in required_keys:
        if key not in params:
            logger.error(f"Отсутствует необходимый параметр: {key}")
            raise KeyError(f"Отсутствует необходимый параметр: {key}")

    server_public_key = params['SERVER_PUB_KEY']
    endpoint = f"{params['SERVER_PUB_IP']}:{params['SERVER_PORT']}"
    dns_servers = f"{params['CLIENT_DNS_1']},{params['CLIENT_DNS_2']}"

    private_key = generate_private_key()
    logger.debug("Приватный ключ сгенерирован.")
    public_key = generate_public_key(private_key).decode()  # Декодируем байты в строку
    logger.debug("Публичный ключ сгенерирован.")
    preshared_key = generate_preshared_key().decode()  # Декодируем байты в строку
    logger.debug("Пресекретный ключ сгенерирован.")

    # Генерация IP-адреса
    existing_ips, new_ipv4 = generate_ip(config_file)
    logger.info(f"Существующие IP: {existing_ips}")
    logger.info(f"Подсеть WireGuard: {params['SERVER_SUBNET']}")
    logger.info(f"IP-адрес сгенерирован: {new_ipv4}")

    # Генерация конфигурации клиента
    client_config = create_client_config(
        private_key=private_key,
        address=new_ipv4,
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

    # Создаем запись пользователя
    user_record = create_user_record(
        username=nickname,
        address=new_ipv4,
        public_key=public_key,
        preshared_key=preshared_key,
        qr_code_path=qr_path,
        email=email,
        telegram_id=telegram_id
    )

    # Сохраняем запись пользователя
    save_user_record(user_record)

    # Добавление пользователя в конфигурацию сервера
    add_user_to_server_config(config_file, nickname, public_key, preshared_key, new_ipv4)
    logger.info("Пользователь добавлен в конфигурацию сервера.")

    return config_path, qr_path


def add_user_to_server_config(config_file, nickname, public_key, preshared_key, allowed_ip):
    """
    Добавляет пользователя в конфигурацию сервера WireGuard.
    """
    try:
        with open(config_file, "a") as file:
            file.write(f"\n### Client {nickname}\n")
            file.write("[Peer]\n")
            file.write(f"PublicKey = {public_key}\n")
            file.write(f"PresharedKey = {preshared_key}\n")
            file.write(f"AllowedIPs = {allowed_ip}/32\n")  # Убедимся, что формат корректен
        logger.info(f"Пользователь {nickname} успешно добавлен в {config_file}")
    except Exception as e:
        logger.error(f"Ошибка добавления пользователя в конфигурацию сервера: {e}")
        raise


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
        restart_wireguard(params['SERVER_WG_NIC'])

    except Exception as e:
        logger.error(f"Ошибка выполнения: {e}")
