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


def restart_wireguard(interface="wg0"):
    """
    Перезапускает WireGuard.
    """
    try:
        subprocess.run(["sudo", "systemctl", "restart", f"wg-quick@{interface}"], check=True)
        print(f"✅ WireGuard {interface} успешно перезапущен.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка перезапуска WireGuard: {e}")


def generate_config(nickname, params, config_file, email="N/A", telegram_id="N/A"):
    """
    Генерация конфигурации пользователя и QR-кода.
    :param nickname: Имя пользователя.
    :param params: Параметры сервера.
    :param config_file: Путь к файлу конфигурации сервера WireGuard.
    :param email: Электронная почта пользователя.
    :param telegram_id: Telegram ID пользователя.
    :return: Пути к файлу конфигурации пользователя и QR-коду.
    """
    server_public_key = params['SERVER_PUB_KEY']
    endpoint = f"{params['SERVER_PUB_IP']}:{params['SERVER_PORT']}"
    dns_servers = f"{params['CLIENT_DNS_1']},{params['CLIENT_DNS_2']}"

    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    preshared_key = generate_preshared_key()

    # Генерация IP-адреса
    address, new_ipv4 = generate_ip(config_file)

    # Используем функцию для генерации конфигурации клиента
    client_config = create_client_config(
        private_key=private_key,
        address=address,
        dns_servers=dns_servers,
        server_public_key=server_public_key,
        preshared_key=preshared_key,
        endpoint=endpoint
    )

    config_path = os.path.join(settings.WG_CONFIG_DIR, f"{nickname}.conf")
    qr_path = os.path.join(settings.QR_CODE_DIR, f"{nickname}.png")

    # Сохраняем конфигурационный файл клиента
    os.makedirs(settings.WG_CONFIG_DIR, exist_ok=True)
    with open(config_path, "w") as file:
        file.write(client_config)

    # Генерация QR-кода
    generate_qr_code(client_config, qr_path)

    # Добавляем нового пользователя в конфигурацию сервера
    add_user_to_server_config(config_file, nickname, public_key.decode('utf-8'), preshared_key.decode('utf-8'), address)

    # Добавляем запись пользователя с дополнительными данными
    add_user_record(
        nickname,
        trial_days=settings.DEFAULT_TRIAL_DAYS,
        address=address,
        public_key=public_key.decode('utf-8'),
        preshared_key=preshared_key.decode('utf-8'),
        qr_code_path=qr_path,
        email=email,
        telegram_id=telegram_id
    )

    # Перезапускаем WireGuard для применения изменений
    restart_wireguard(params['SERVER_WG_NIC'])

    return config_path, qr_path


def add_user_record(nickname, trial_days, address, public_key, preshared_key, qr_code_path, email, telegram_id):
    """
    Добавляет запись о пользователе с расширенными данными.
    """
    user_records_path = os.path.join("user", "data", "user_records.json")
    expiry_date = datetime.now() + timedelta(days=trial_days)

    # Загружаем существующие записи
    if os.path.exists(user_records_path):
        with open(user_records_path, "r", encoding="utf-8") as file:
            try:
                user_data = json.load(file)
            except json.JSONDecodeError:
                user_data = {}
    else:
        user_data = {}

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
        "qr_code_path": qr_code_path,
        "email": email,
        "telegram_id": telegram_id,
        "status": "inactive"  # будет обновляться позже
    }

    # Сохраняем обновленные данные
    os.makedirs(os.path.dirname(user_records_path), exist_ok=True)
    with open(user_records_path, "w", encoding="utf-8") as file:
        json.dump(user_data, file, indent=4)
    print(f"✅ Данные пользователя {nickname} успешно добавлены в {user_records_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 main.py <nickname> [email] [telegram_id]")
        sys.exit(1)

    nickname = sys.argv[1]
    email = sys.argv[2] if len(sys.argv) > 2 else "N/A"
    telegram_id = sys.argv[3] if len(sys.argv) > 3 else "N/A"
    params_file = settings.PARAMS_FILE

    try:
        setup_directories()  # Вызов функции для проверки и создания директорий

        params = load_params(params_file)  # Загружаем параметры из файла
        config_file = settings.SERVER_CONFIG_FILE
        config_path, qr_path = generate_config(nickname, params, config_file, email, telegram_id)
        print(f"Конфигурация сохранена в {config_path}")
        print(f"QR-код сохранён в {qr_path}")
    except Exception as e:
        print(f"Ошибка: {e}")
