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
from modules.main_registration_fields import create_user_record  # Подключаем новую функцию
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
                logger.warning("Ошибка чтения базы данных пользователей, будет создана новая.")
                return {}
    return {}

def add_user_record(user_record):
    """
    Сохраняет запись о пользователе в JSON-файл.
    """
    logger.info(f"Добавление записи пользователя {user_record['username']} в базу данных.")
    user_records_path = os.path.join("user", "data", "user_records.json")

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
    if user_record["username"] in user_data:
        logger.error(f"Пользователь с именем '{user_record['username']}' уже существует в базе данных.")
        raise ValueError(f"Пользователь с именем '{user_record['username']}' уже существует.")

    # Добавляем новую запись
    user_data[user_record["username"]] = user_record

    # Сохраняем обновленные данные
    os.makedirs(os.path.dirname(user_records_path), exist_ok=True)
    with open(user_records_path, "w", encoding="utf-8") as file:
        json.dump(user_data, file, indent=4)
    logger.info(f"Данные пользователя {user_record['username']} успешно добавлены в {user_records_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Недостаточно аргументов. Использование: python3 main.py <nickname> [email] [telegram_id] [referral_id] [coupon_id]")
        sys.exit(1)

    nickname = sys.argv[1]
    email = sys.argv[2] if len(sys.argv) > 2 else "N/A"
    telegram_id = sys.argv[3] if len(sys.argv) > 3 else "N/A"
    referral_id = sys.argv[4] if len(sys.argv) > 4 else None
    coupon_id = sys.argv[5] if len(sys.argv) > 5 else None
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
        private_key = generate_private_key()
        public_key = generate_public_key(private_key).decode()
        preshared_key = generate_preshared_key().decode()
        address, _ = generate_ip(config_file)

        qr_path = os.path.join(settings.QR_CODE_DIR, f"{nickname}.png")
        generate_qr_code("dummy_config_for_test", qr_path)  # Здесь замените на реальную конфигурацию

        user_record = create_user_record(
            username=nickname,
            address=address,
            public_key=public_key,
            preshared_key=preshared_key,
            qr_code_path=qr_path,
            email=email,
            telegram_id=telegram_id,
            referral_id=referral_id,
            coupon_id=coupon_id
        )

        add_user_record(user_record)

        logger.info(f"✅ Конфигурация сохранена.")
        logger.info(f"✅ QR-код сохранён в {qr_path}")
    except Exception as e:
        logger.error(f"Ошибка выполнения: {e}")
