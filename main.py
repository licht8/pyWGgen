import sys
import os
import settings

from modules.config import load_params
from modules.keygen import generate_private_key, generate_public_key, generate_preshared_key
from modules.ip_management import get_existing_ips, generate_ip
from modules.config_writer import add_user_to_server_config
from modules.sync import sync_wireguard_config
from modules.qr_generator import generate_qr_code
from modules.user_management import add_user_record
from modules.directory_setup import setup_directories
from modules.client_config import create_client_config


def generate_config(nickname, params, config_file):
    server_public_key = params['SERVER_PUB_KEY']
    endpoint = f"{params['SERVER_PUB_IP']}:{params['SERVER_PORT']}"
    dns_servers = f"{params['CLIENT_DNS_1']},{params['CLIENT_DNS_2']}"

    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    preshared_key = generate_preshared_key()

    existing_ips = get_existing_ips(config_file)
    address, new_ipv4 = generate_ip(existing_ips)

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

    # Добавляем запись пользователя с датой создания и удаления
    add_user_record(nickname, trial_days=settings.DEFAULT_TRIAL_DAYS, address=address)

    return config_path, qr_path

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python3 main.py <nickname>")
        sys.exit(1)

    nickname = sys.argv[1]
    params_file = settings.PARAMS_FILE

    try:
        setup_directories()  # Вызов функции для проверки и создания директорий

        params = load_params(params_file)  # Загружаем параметры из файла
        config_file = settings.SERVER_CONFIG_FILE
        config_path, qr_path = generate_config(nickname, params, config_file)
        print(f"Конфигурация сохранена в {config_path}")
        print(f"QR-код сохранен в {qr_path}")

        # Синхронизация конфигурации сервера
        sync_wireguard_config(params['SERVER_WG_NIC'])  # Передаем имя интерфейса WireGuard

    except Exception as e:
        print(f"Ошибка: {e}")
