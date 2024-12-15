#!/usr/bin/env python3
# modules/install_wg.py
# ===========================================
# Установщик WireGuard с полной поддержкой параметров
# Версия 2.7
# ===========================================
# Назначение:
# - Установка и настройка WireGuard на CentOS 8 / CentOS Stream 8.
# - Генерация конфигурационного файла wg0.conf.
# - Создание параметров в файле /etc/wireguard/params.
# - Запись пользовательских параметров в .env.
# - Настройка firewalld для работы с WireGuard.
#
# Особенности:
# - Поддержка интерактивного ввода подсети и порта.
# - Полная совместимость с bash-скриптом по функционалу.
# ===========================================

import os
import subprocess
import shutil
from pathlib import Path
import ipaddress
from modules.firewall_utils import get_external_ip
from settings import DEFAULT_SUBNET, WIREGUARD_PORT, SERVER_CONFIG_FILE, PARAMS_FILE

ENV_FILE = Path(".env")

def log_message(message: str, level: str = "INFO"):
    """Логирует сообщение."""
    print(f"{level}: {message}")

def is_root():
    """Проверяет запуск от имени root."""
    if os.geteuid() != 0:
        raise PermissionError("Скрипт должен быть запущен от имени root.")

def check_os():
    """Проверяет, что ОС является CentOS 8 или CentOS Stream 8."""
    with open("/etc/os-release") as f:
        os_info = f.read()
    if not (("CentOS" in os_info and "8" in os_info) or "CentOS Stream 8" in os_info):
        raise EnvironmentError("Требуется CentOS Linux 8 или CentOS Stream 8.")

def create_wireguard_directory():
    """Создает директорию /etc/wireguard, если она отсутствует."""
    wg_dir = Path("/etc/wireguard")
    if not wg_dir.exists():
        wg_dir.mkdir(mode=0o700, parents=True)
        log_message("Создана директория /etc/wireguard")

def detect_server_ip_and_nic():
    """Определяет публичный IP-адрес и сетевой интерфейс сервера."""
    try:
        # Определение сетевого интерфейса (NIC)
        server_pub_nic = subprocess.check_output(
            ["ip", "route", "show", "default"], text=True
        ).split()[4]

        # Получение публичного IP-адреса через get_external_ip
        server_pub_ip = get_external_ip()

        if not server_pub_ip or server_pub_ip.startswith("N/A"):
            raise RuntimeError("Не удалось определить внешний IP-адрес.")
        return server_pub_ip, server_pub_nic
    except (IndexError, subprocess.CalledProcessError) as e:
        raise RuntimeError(f"Ошибка определения IP-адреса или сетевого интерфейса: {e}")

def write_env_file(subnet, port):
    """Создает файл .env с пользовательскими параметрами."""
    dns = "1.1.1.1, 1.0.0.1, 8.8.8.8"
    env_content = f"""
# Параметры WireGuard (установленное пользователем)
WIREGUARD_PORT={port}
DEFAULT_SUBNET="{DEFAULT_SUBNET}"
USER_SET_SUBNET="{subnet}"
DNS_WIREGUARD="{dns}"
"""
    with open(ENV_FILE, "w") as env_file:
        env_file.write(env_content.strip() + "\n")  # Гарантируем переход на новую строку
    log_message(f"Файл .env создан: {ENV_FILE}")

def write_params_file(subnet, port, private_key, public_key):
    """Создает файл /etc/wireguard/params с параметрами сервера."""
    server_pub_ip, server_pub_nic = detect_server_ip_and_nic()

    # Убедимся, что SERVER_WG_IPV4 корректно использует первый IP из подсети
    server_wg_ipv4 = str(ipaddress.ip_network(subnet, strict=False).network_address + 1)

    params_content = f"""
SERVER_PUB_IP={server_pub_ip}
SERVER_PUB_NIC={server_pub_nic}
SERVER_WG_NIC=wg0
SERVER_WG_IPV4={server_wg_ipv4}
SERVER_WG_IPV6=fd42:42:42::1
SERVER_PORT={port}
SERVER_PRIV_KEY={private_key}
SERVER_PUB_KEY={public_key}
CLIENT_DNS_1=1.1.1.1
CLIENT_DNS_2=1.0.0.1
"""
    with open(PARAMS_FILE, "w") as params_file:
        params_file.write(params_content.strip() + "\n")  # Гарантируем переход на новую строку
    os.chmod(PARAMS_FILE, 0o600)
    log_message(f"Файл параметров создан: {PARAMS_FILE}")

def validate_subnet(subnet):
    """Проверяет корректность подсети."""
    try:
        ipaddress.ip_network(subnet, strict=True)
        return subnet
    except ValueError:
        raise ValueError(f"Некорректная подсеть: {subnet}")

def prompt_parameters():
    """Запрашивает параметры WireGuard у пользователя."""
    subnet = input(f"Введите подсеть WireGuard [{DEFAULT_SUBNET}]: ") or DEFAULT_SUBNET
    subnet = validate_subnet(subnet)

    port = input(f"Введите порт WireGuard [{WIREGUARD_PORT}]: ") or WIREGUARD_PORT
    port = int(port)

    return subnet, port

def generate_keypair():
    """Генерирует приватный и публичный ключи."""
    wg_path = shutil.which("wg")
    if not wg_path:
        raise RuntimeError("WireGuard не установлен. Установите его перед началом.")
    private_key = subprocess.check_output([wg_path, "genkey"]).decode().strip()
    public_key = subprocess.check_output([wg_path, "pubkey"], input=private_key.encode()).decode().strip()
    return private_key, public_key

def generate_wg_config(subnet, port):
    """Генерирует конфигурацию WireGuard."""
    base_subnet = subnet.split("/")[0]
    server_private_key, server_public_key = generate_keypair()

    server_pub_ip, server_pub_nic = detect_server_ip_and_nic()

    server_config = f"""
[Interface]
Address = {subnet},fd42:42:42::1/64
ListenPort = {port}
PrivateKey = {server_private_key}
PostUp = firewall-cmd --add-port {port}/udp && firewall-cmd --add-rich-rule='rule family=ipv4 source address={base_subnet}/24 masquerade' && firewall-cmd --add-rich-rule='rule family=ipv6 source address=fd42:42:42::0/64 masquerade'
PostDown = firewall-cmd --remove-port {port}/udp && firewall-cmd --remove-rich-rule='rule family=ipv4 source address={base_subnet}/24 masquerade' && firewall-cmd --remove-rich-rule='rule family=ipv6 source address=fd42:42:42::0/64 masquerade'
    """
    with open(SERVER_CONFIG_FILE, "w") as config_file:
        config_file.write(server_config)

    write_params_file(subnet, port, server_private_key, server_public_key)
    write_env_file(subnet, port)
    return server_private_key, server_public_key

def configure_firewalld(port, subnet):
    """Настраивает firewalld."""
    base_subnet = subnet.split("/")[0]
    subprocess.run(["firewall-cmd", "--add-port", f"{port}/udp", "--permanent"], check=True)
    subprocess.run(["firewall-cmd", "--add-rich-rule", f"rule family=ipv4 source address={base_subnet}/24 masquerade", "--permanent"], check=True)
    subprocess.run(["firewall-cmd", "--add-rich-rule", "rule family=ipv6 source address=fd42:42:42::0/64 masquerade", "--permanent"], check=True)
    subprocess.run(["firewall-cmd", "--reload"], check=True)

def enable_and_start_service(port):
    """Активирует и запускает WireGuard."""
    service_name = f"wg-quick@wg0"
    subprocess.run(["systemctl", "enable", service_name], check=True)
    subprocess.run(["systemctl", "start", service_name], check=True)
    log_message(f"WireGuard успешно запущен на порту {port}.")

def install_wireguard_packages():
    """Устанавливает все необходимые пакеты для WireGuard."""
    log_message("Установка пакетов для WireGuard...")
    try:
        subprocess.run(["dnf", "install", "-y", "epel-release", "elrepo-release"], check=True)
        subprocess.run(["dnf", "install", "-y", "wireguard-tools", "kmod-wireguard", "qrencode", "iptables"], check=True)
        log_message("Все пакеты успешно установлены.")
    except subprocess.CalledProcessError as e:
        log_message(f"Ошибка при установке пакетов: {e}", level="ERROR")
        raise

def install_wireguard():
    """Устанавливает WireGuard с настройками."""
    try:
        is_root()
        check_os()
        create_wireguard_directory()

        subnet, port = prompt_parameters()

        install_wireguard_packages()

        generate_wg_config(subnet, port)
        configure_firewalld(port, subnet)
        enable_and_start_service(port)

        log_message("✅ Установка WireGuard завершена.")
    except Exception as e:
        log_message(f"Ошибка: {e}", level="ERROR")

if __name__ == "__main__":
    install_wireguard()
