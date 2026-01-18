#!/usr/bin/env python3
# modules/install_wg.py
# ===========================================
# Instalator WireGuard z pełnym wsparciem parametrów
# Wersja 2.8
# ===========================================
# Cel:
# - Instalacja i konfiguracja WireGuard na CentOS 8 / CentOS Stream 8.
# - Generowanie pliku konfiguracyjnego wg0.conf.
# - Tworzenie parametrów w pliku /etc/wireguard/params.
# - Zapis parametrów użytkownika w pliku .env.
# - Konfiguracja firewalld dla WireGuard.
#
# Funkcje:
# - Obsługa interaktywnego wprowadzania podsieci i portu.
# - Pełna kompatybilność z funkcjonalnością skryptu bash.
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
    """Loguje wiadomość."""
    print(f"{level}: {message}")

def is_root():
    """Sprawdza czy skrypt jest uruchamiany jako root."""
    if os.geteuid() != 0:
        raise PermissionError("Skrypt musi być uruchomiony jako root.")

def check_os():
    """Sprawdza czy system to CentOS 8 lub CentOS Stream 8."""
    with open("/etc/os-release") as f:
        os_info = f.read()
    if not (("CentOS" in os_info and "8" in os_info) or "CentOS Stream 8" in os_info):
        raise EnvironmentError("Wymagany jest CentOS Linux 8 lub CentOS Stream 8.")

def create_wireguard_directory():
    """Tworzy katalog /etc/wireguard jeśli nie istnieje."""
    wg_dir = Path("/etc/wireguard")
    if not wg_dir.exists():
        wg_dir.mkdir(mode=0o700, parents=True)
        log_message("Utworzono katalog /etc/wireguard")

def detect_server_ip_and_nic():
    """Wykrywa publiczny adres IP serwera i interfejs sieciowy."""
    try:
        server_pub_nic = subprocess.check_output(
            ["ip", "route", "show", "default"], text=True
        ).split()[4]

        server_pub_ip = get_external_ip()

        if not server_pub_ip or server_pub_ip.startswith("N/A"):
            raise RuntimeError("Nie udało się określić zewnętrznego adresu IP.")
        return server_pub_ip, server_pub_nic
    except (IndexError, subprocess.CalledProcessError) as e:
        raise RuntimeError(f"Błąd określania adresu IP lub interfejsu sieciowego: {e}")

def write_env_file(subnet, port):
    """Tworzy plik .env z parametrami użytkownika."""
    dns = "1.1.1.1, 1.0.0.1, 8.8.8.8"
    env_content = f"""
# Parametry WireGuard (ustawione przez użytkownika)
WIREGUARD_PORT={port}
DEFAULT_SUBNET="{DEFAULT_SUBNET}"
USER_SET_SUBNET="{subnet}"
DNS_WIREGUARD="{dns}"
"""
    with open(ENV_FILE, "w") as env_file:
        env_file.write(env_content.strip() + "\n")  # Zapewnia nową linię na końcu
    log_message(f"Utworzono plik .env: {ENV_FILE}")

def write_params_file(subnet, port, private_key, public_key):
    """Tworzy plik /etc/wireguard/params z parametrami serwera."""
    server_pub_ip, server_pub_nic = detect_server_ip_and_nic()

    # Upewnia się, że SERVER_WG_IPV4 używa pierwszego IP z podsieci
    server_wg_ipv4 = str(ipaddress.ip_network(subnet, strict=False).network_address + 1)

    params_content = f"""
[serwer]
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
        params_file.write(params_content.strip() + "\n")  # Zapewnia nową linię na końcu
    os.chmod(PARAMS_FILE, 0o600)
    log_message(f"Utworzono plik parametrów: {PARAMS_FILE}")

def validate_subnet(subnet):
    """Waliduje podsieć."""
    try:
        ipaddress.ip_network(subnet, strict=True)
        return subnet
    except ValueError:
        raise ValueError(f"Nieprawidłowa podsieć: {subnet}")

def prompt_parameters():
    """Pyta użytkownika o parametry WireGuard."""
    subnet = input(f"Wprowadź podsieć WireGuard [{DEFAULT_SUBNET}]: ") or DEFAULT_SUBNET
    subnet = validate_subnet(subnet)

    port = input(f"Wprowadź port WireGuard [{WIREGUARD_PORT}]: ") or WIREGUARD_PORT
    port = int(port)

    return subnet, port

def generate_keypair():
    """Generuje klucze prywatny i publiczny."""
    wg_path = shutil.which("wg")
    if not wg_path:
        raise RuntimeError("WireGuard nie jest zainstalowany. Zainstaluj go przed kontynuacją.")
    private_key = subprocess.check_output([wg_path, "genkey"]).decode().strip()
    public_key = subprocess.check_output([wg_path, "pubkey"], input=private_key.encode()).decode().strip()
    return private_key, public_key

def generate_wg_config(subnet, port):
    """Generuje konfigurację WireGuard."""
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
    """Konfiguruje firewalld."""
    base_subnet = subnet.split("/")[0]
    subprocess.run(["firewall-cmd", "--add-port", f"{port}/udp", "--permanent"], check=True)
    subprocess.run(["firewall-cmd", "--add-rich-rule", f"rule family=ipv4 source address={base_subnet}/24 masquerade", "--permanent"], check=True)
    subprocess.run(["firewall-cmd", "--add-rich-rule", "rule family=ipv6 source address=fd42:42:42::0/64 masquerade", "--permanent"], check=True)
    subprocess.run(["firewall-cmd", "--reload"], check=True)

def enable_and_start_service(port):
    """Włącza i uruchamia WireGuard."""
    service_name = f"wg-quick@wg0"
    subprocess.run(["systemctl", "enable", service_name], check=True)
    subprocess.run(["systemctl", "start", service_name], check=True)
    log_message(f"WireGuard pomyślnie uruchomiony na porcie {port}.")

def install_wireguard_packages():
    """Instaluje wszystkie niezbędne pakiety dla WireGuard."""
    log_message("Instalowanie pakietów dla WireGuard...")
    try:
        subprocess.run(["dnf", "install", "-y", "epel-release", "elrepo-release"], check=True)
        subprocess.run(["dnf", "install", "-y", "wireguard-tools", "kmod-wireguard", "qrencode", "iptables"], check=True)
        log_message("Wszystkie pakiety zainstalowane pomyślnie.")
    except subprocess.CalledProcessError as e:
        log_message(f"Błąd instalacji pakietów: {e}", level="ERROR")
        raise

def install_wireguard():
    """Instaluje WireGuard z konfiguracją."""
    try:
        is_root()
        check_os()
        create_wireguard_directory()

        subnet, port = prompt_parameters()

        install_wireguard_packages()

        generate_wg_config(subnet, port)
        configure_firewalld(port, subnet)
        enable_and_start_service(port)

        log_message("✅ Instalacja WireGuard zakończona.")
    except Exception as e:
        log_message(f"Błąd: {e}", level="ERROR")

if __name__ == "__main__":
    install_wireguard()
