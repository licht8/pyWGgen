#!/usr/bin/env python3
# main.py
## Версия: 1.0
## Основной скрипт для создания пользователей WireGuard
##
## Этот скрипт автоматически генерирует конфигурации для новых пользователей,
## включая уникальные ключи, IP-адрес, и QR-код. Скрипт рассчитывает подсеть
## на основе IP-адреса сервера (SERVER_WG_IPV4) и перезапускает интерфейс WireGuard.

import sys
import os
import json
import ipaddress
from datetime import datetime
import settings
from modules.config import load_params
from modules.keygen import generate_private_key, generate_public_key, generate_preshared_key
from modules.config_writer import add_user_to_server_config
from modules.directory_setup import setup_directories
from modules.client_config import create_client_config
from modules.main_registration_fields import create_user_record  # Импорт новой функции
import subprocess
import logging
import qrcode

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

def calculate_subnet(server_wg_ipv4, default_subnet="10.66.66.0/24"):
    """
    Рассчитывает подсеть на основе IP-адреса сервера WireGuard.
    :param server_wg_ipv4: IP-адрес сервера WireGuard.
    :param default_subnet: Подсеть по умолчанию.
    :return: Подсеть в формате CIDR (например, '10.66.66.0/24').
    """
    try:
        ip = ipaddress.ip_interface(f"{server_wg_ipv4}/24")
        subnet = str(ip.network)
        logger.debug(f"Подсеть рассчитана на основе SERVER_WG_IPV4: {subnet}")
        return subnet
    except ValueError as e:
        logger.warning(f"Ошибка при расчете подсети: {e}. Используется значение по умолчанию: {default_subnet}")
        return default_subnet

def generate_next_ip(config_file, subnet="10.66.66.0/24"):
    """
    Генерирует следующий доступный IP-адрес в подсети.
    :param config_file: Путь к файлу конфигурации WireGuard.
    :param subnet: Подсеть для поиска доступного IP.
    :return: Следующий доступный IP-адрес.
    """
    logger.debug(f"Ищем свободный IP-адрес в подсети {subnet}.")
    existing_ips = []
    if os.path.exists(config_file):
        logger.debug(f"Чтение существующих IP-адресов из файла {config_file}.")
        with open(config_file, "r") as f:
            for line in f:
                if line.strip().startswith("AllowedIPs"):
                    ip = line.split("=")[1].strip().split("/")[0]
                    existing_ips.append(ip)
    network = ipaddress.ip_network(subnet)
    for ip in network.hosts():
        ip_str = str(ip)
        if ip_str not in existing_ips and not ip_str.endswith(".0") and not ip_str.endswith(".1") and not ip_str.endswith(".255"):
            logger.debug(f"Свободный IP-адрес найден: {ip_str}")
            return ip_str
    logger.error("Нет доступных IP-адресов в указанной подсети.")
    raise ValueError("Нет доступных IP-адресов в указанной подсети.")

def generate_qr_code(data, output_path):
    """
    Генерирует QR-код на основе данных конфигурации.
    :param data: Текстовая конфигурация WireGuard.
    :param output_path: Путь для сохранения изображения QR-кода.
    """
    logger.debug(f"Генерация QR-кода для данных длиной {len(data)} символов.")
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)
        logger.info(f"QR-код успешно сохранён в {output_path}")
    except Exception as e:
        logger.error(f"Ошибка при генерации QR-кода: {e}")
        raise

def load_existing_users():
    """
    Загружает список существующих пользователей из базы данных.
    """
    user_records_path = os.path.join("user", "data", "user_records.json")
    logger.debug(f"Загрузка базы пользователей из {user_records_path}")
    if os.path.exists(user_records_path):
        with open(user_records_path, "r", encoding="utf-8") as file:
            try:
                user_data = json.load(file)
                logger.info(f"Успешно загружено {len(user_data)} пользователей.")
                return {user.lower(): user_data[user] for user in user_data}  # Нормализуем имена
            except json.JSONDecodeError as e:
                logger.warning(f"Ошибка чтения базы данных: {e}. Возвращаем пустую базу.")
                return {}
    logger.warning(f"Файл базы данных {user_records_path} не найден.")
    return {}

def is_user_in_server_config(nickname, config_file):
    """
    Проверяет наличие пользователя в конфигурации сервера.
    """
    nickname_lower = nickname.lower()
    logger.debug(f"Проверка наличия пользователя {nickname} в конфигурации {config_file}.")
    try:
        with open(config_file, "r") as file:
            for line in file:
                if nickname_lower in line.lower():
                    logger.info(f"Пользователь {nickname} найден в конфигурации сервера.")
                    return True
    except FileNotFoundError:
        logger.warning(f"Файл конфигурации {config_file} не найден.")
    return False

def restart_wireguard(interface="wg0"):
    """
    Перезапускает WireGuard и показывает его статус.
    """
    try:
        logger.info(f"Перезапуск интерфейса WireGuard: {interface}")
        subprocess.run(["sudo", "systemctl", "restart", f"wg-quick@{interface}"], check=True)
        logger.info(f"{WG_EMOJI} WireGuard интерфейс {interface} успешно перезапущен.")

        # Получение статуса WireGuard
        wg_status = subprocess.check_output(["sudo", "systemctl", "status", f"wg-quick@{interface}"]).decode()
        for line in wg_status.splitlines():
            if "Active:" in line:
                logger.info(f"{WG_EMOJI} Статус WireGuard: {line.strip()}")

        # Вывод состояния firewall
        firewall_status = subprocess.check_output(["sudo", "firewall-cmd", "--list-ports"]).decode()
        for line in firewall_status.splitlines():
            logger.info(f"{FIREWALL_EMOJI} Состояние firewall: {line.strip()}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка перезапуска WireGuard: {e}")

def generate_config(nickname, params, config_file, email="N/A", telegram_id="N/A"):
    """
    Генерация конфигурации пользователя и QR-кода.
    """
    logger.info("+--------- Процесс 🌱 создания пользователя активирован ---------+")
    try:
        logger.info(f"{INFO_EMOJI} Начало генерации конфигурации для пользователя: {nickname}")
        
        # Проверка наличия SERVER_PUB_IP
        server_public_key = params['SERVER_PUB_KEY']
        if not params.get('SERVER_PUB_IP'):
            raise ValueError("Параметр SERVER_PUB_IP отсутствует. Проверьте файл конфигурации.")
        
        endpoint = f"{params['SERVER_PUB_IP']}:{params['SERVER_PORT']}"
        dns_servers = f"{params['CLIENT_DNS_1']},{params['CLIENT_DNS_2']}"

        private_key = generate_private_key()
        logger.debug(f"{DEBUG_EMOJI} Приватный ключ успешно сгенерирован.")
        public_key = generate_public_key(private_key)
        logger.debug(f"{DEBUG_EMOJI} Публичный ключ успешно сгенерирован.")
        preshared_key = generate_preshared_key()
        logger.debug(f"{DEBUG_EMOJI} Пресекретный ключ успешно сгенерирован.")

        # Вычисление подсети
        subnet = calculate_subnet(params.get('SERVER_WG_IPV4', '10.66.66.1'))
        logger.debug(f"{DEBUG_EMOJI} Используемая подсеть: {subnet}")

        # Генерация IP-адреса
        new_ipv4 = generate_next_ip(config_file, subnet)
        logger.info(f"{INFO_EMOJI} Новый IP-адрес пользователя: {new_ipv4}")

        # Генерация конфигурации клиента
        client_config = create_client_config(
            private_key=private_key,
            address=new_ipv4,
            dns_servers=dns_servers,
            server_public_key=server_public_key,
            preshared_key=preshared_key,
            endpoint=endpoint
        )
        logger.debug(f"{DEBUG_EMOJI} Конфигурация клиента успешно создана.")

        config_path = os.path.join(settings.WG_CONFIG_DIR, f"{nickname}.conf")
        qr_path = os.path.join(settings.QR_CODE_DIR, f"{nickname}.png")

        # Сохраняем конфигурацию
        os.makedirs(settings.WG_CONFIG_DIR, exist_ok=True)
        with open(config_path, "w") as file:
            file.write(client_config)
        logger.info(f"{INFO_EMOJI} Конфигурация пользователя сохранена в {config_path}")

        # Генерация QR-кода
        generate_qr_code(client_config, qr_path)
        logger.info(f"{INFO_EMOJI} QR-код пользователя сохранён в {qr_path}")

        # Добавление пользователя в конфигурацию сервера
        add_user_to_server_config(config_file, nickname, public_key.decode('utf-8'), preshared_key.decode('utf-8'), new_ipv4)
        logger.info(f"{INFO_EMOJI} Пользователь успешно добавлен в конфигурацию сервера.")

        # Добавление записи пользователя
        user_record = create_user_record(
            username=nickname,
            address=new_ipv4,
            public_key=public_key.decode('utf-8'),
            preshared_key=preshared_key.decode('utf-8'),
            qr_code_path=qr_path,
            email=email,
            telegram_id=telegram_id
        )
        logger.debug(f"{DEBUG_EMOJI} Запись пользователя сформирована.")

        # Сохраняем в базе данных
        user_records_path = os.path.join("user", "data", "user_records.json")
        os.makedirs(os.path.dirname(user_records_path), exist_ok=True)
        with open(user_records_path, "r+", encoding="utf-8") as file:
            try:
                user_data = json.load(file)
                logger.debug(f"{DEBUG_EMOJI} Загружены существующие записи пользователей.")
            except json.JSONDecodeError:
                user_data = {}
                logger.warning(f"{WARNING_EMOJI} Ошибка чтения базы данных пользователей, будет создана новая.")
            user_data[nickname] = user_record
            file.seek(0)
            json.dump(user_data, file, indent=4)
            file.truncate()
        logger.info(f"{INFO_EMOJI} Данные пользователя {nickname} успешно добавлены в {user_records_path}")

        # Синхронизация WireGuard
        try:
            stripped_config = subprocess.check_output(['wg-quick', 'strip', 'wg0'])
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(stripped_config)
                temp_file.flush()
                subprocess.run(['wg', 'syncconf', 'wg0', temp_file.name], check=True)
            logger.info(f"{WG_EMOJI} Конфигурация WireGuard успешно синхронизирована.")
        except subprocess.CalledProcessError as e:
            logger.error(f"{ERROR_EMOJI} Ошибка при синхронизации конфигурации WireGuard: {e}")
            raise
        except Exception as e:
            logger.error(f"{ERROR_EMOJI} Непредвиденная ошибка при синхронизации WireGuard: {e}")
            raise

        logger.info("+--------- Процесс 🌱 создания пользователя завершен --------------+\n")
        return config_path, qr_path
    except Exception as e:
        logger.error(f"{ERROR_EMOJI} Ошибка выполнения: {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Недостаточно аргументов. Использование: python3 main.py <nickname> [email] [telegram_id]")
        sys.exit(1)

    nickname = sys.argv[1]
    email = sys.argv[2] if len(sys.argv) > 2 else "N/A"
    telegram_id = sys.argv[3] if len(sys.argv) > 3 else "N/A"
    params_file = settings.PARAMS_FILE

    logger.info("Запуск процесса создания нового пользователя WireGuard.")
    try:
        logger.info("Инициализация директорий.")
        setup_directories()

        logger.info(f"Загрузка параметров из файла: {params_file}")
        params = load_params(params_file)

        logger.info("Проверка существующего пользователя.")
        existing_users = load_existing_users()
        if nickname.lower() in existing_users:
            logger.error(f"Пользователь с именем '{nickname}' уже существует в базе данных.")
            sys.exit(1)

        if is_user_in_server_config(nickname, settings.SERVER_CONFIG_FILE):
            logger.error(f"Пользователь с именем '{nickname}' уже существует в конфигурации сервера.")
            sys.exit(1)

        logger.info("Генерация конфигурации пользователя.")
        config_file = settings.SERVER_CONFIG_FILE
        config_path, qr_path = generate_config(nickname, params, config_file, email, telegram_id)

        logger.info(f"✅ Конфигурация пользователя сохранена в {config_path}")
        logger.info(f"✅ QR-код пользователя сохранён в {qr_path}")
    except FileNotFoundError as e:
        logger.error(f"Файл не найден: {e}")
    except KeyError as e:
        logger.error(f"Отсутствует ключ в параметрах: {e}")
    except ValueError as e:
        logger.error(f"Ошибка в значении параметров: {e}")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
