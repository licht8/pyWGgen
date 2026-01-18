#!/usr/bin/env python3
# main.py
## Wersja: 1.0
## Główny skrypt do tworzenia użytkowników WireGuard
##
## Ten skrypt automatycznie generuje konfiguracje dla nowych użytkowników,
## włączając unikalne klucze, adres IP oraz kod QR. Skrypt oblicza podsieć
## na podstawie adresu IP serwera (SERVER_WG_IPV4) i synchronizuje interfejs WireGuard.

import sys
import os
import json
import ipaddress
from datetime import datetime
import settings
from modules.config import load_params
from modules.keygen import generate_private_key, generate_public_key, generate_preshared_key
from modules.directory_setup import setup_directories
from modules.client_config import create_client_config
from modules.main_registration_fields import create_user_record  # Import nowej funkcji
import subprocess
import logging
import qrcode
import tempfile

# Konfiguracja loggera
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
    Oblicza podsieć na podstawie adresu IP serwera WireGuard.
    :param server_wg_ipv4: Adres IP serwera WireGuard.
    :param default_subnet: Domyślna podsieć.
    :return: Podsieć w formacie CIDR (np. '10.66.66.0/24').
    """
    try:
        ip = ipaddress.ip_interface(f"{server_wg_ipv4}/24")
        subnet = str(ip.network)
        logger.debug(f"Podsieć obliczona na podstawie SERVER_WG_IPV4: {subnet}")
        return subnet
    except ValueError as e:
        logger.warning(f"Błąd obliczania podsieci: {e}. Używam wartości domyślnej: {default_subnet}")
        return default_subnet

def generate_next_ip(config_file, subnet="10.66.66.0/24"):
    """
    Generuje następny dostępny adres IP w podsieci.
    :param config_file: Ścieżka do pliku konfiguracyjnego WireGuard.
    :param subnet: Podsieć do wyszukiwania wolnych IP.
    :return: Następny dostępny adres IP.
    """
    logger.debug(f"Wyszukiwanie wolnego adresu IP w podsieci {subnet}.")
    existing_ips = []
    if os.path.exists(config_file):
        logger.debug(f"Odczytywanie istniejących adresów IP z pliku {config_file}.")
        with open(config_file, "r") as f:
            for line in f:
                if line.strip().startswith("AllowedIPs"):
                    ip = line.split("=")[1].strip().split("/")[0]
                    existing_ips.append(ip)
    network = ipaddress.ip_network(subnet)
    for ip in network.hosts():
        ip_str = str(ip)
        if ip_str not in existing_ips and not ip_str.endswith(".0") and not ip_str.endswith(".1") and not ip_str.endswith(".255"):
            logger.debug(f"Znaleziono wolny adres IP: {ip_str}")
            return ip_str
    logger.error("Brak dostępnych adresów IP w określonej podsieci.")
    raise ValueError("Brak dostępnych adresów IP w określonej podsieci.")

def generate_qr_code(data, output_path):
    """
    Generuje kod QR na podstawie danych konfiguracyjnych.
    :param data: Tekst konfiguracji WireGuard.
    :param output_path: Ścieżka do zapisania obrazu kodu QR.
    """
    logger.debug(f"Generowanie kodu QR dla danych o długości {len(data)} znaków.")
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

    except Exception as e:
        logger.error(f"Błąd generowania kodu QR: {e}")
        raise

def load_existing_users():
    """
    Wczytuje listę istniejących użytkowników z bazy danych.
    """
    user_records_path = os.path.join("user", "data", "user_records.json")
    logger.debug(f"Wczytywanie bazy danych użytkowników z {user_records_path}")
    if os.path.exists(user_records_path):
        with open(user_records_path, "r", encoding="utf-8") as file:
            try:
                user_data = json.load(file)
                logger.info(f"Pomyślnie wczytano {len(user_data)} użytkowników.")
                return {user.lower(): user_data[user] for user in user_data}  # Normalizacja nazw
            except json.JSONDecodeError as e:
                logger.warning(f"Błąd odczytu bazy danych: {e}. Zwracam pustą bazę.")
                return {}
    logger.warning(f"Nie znaleziono pliku bazy danych użytkowników {user_records_path}.")
    return {}

def is_user_in_server_config(nickname, config_file):
    """
    Sprawdza czy użytkownik istnieje w konfiguracji serwera.
    """
    nickname_lower = nickname.lower()
    logger.debug(f"Sprawdzanie czy użytkownik {nickname} istnieje w konfiguracji {config_file}.")
    try:
        with open(config_file, "r") as file:
            for line in file:
                if nickname_lower in line.lower():
                    logger.info(f"Użytkownik {nickname} znaleziony w konfiguracji serwera.")
                    return True
    except FileNotFoundError:
        logger.warning(f"Nie znaleziono pliku konfiguracyjnego {config_file}.")
    return False

'''
def restart_wireguard(interface="wg0"):
    """
    Restartuje WireGuard i wyświetla jego status.
    """
    try:
        logger.info(f"Restartowanie interfejsu WireGuard: {interface}")
        subprocess.run(["sudo", "systemctl", "restart", f"wg-quick@{interface}"], check=True)
        logger.info(f"{WG_EMOJI} Interfejs WireGuard {interface} pomyślnie zrestartowany.")

        # Pobierz status WireGuard
        wg_status = subprocess.check_output(["sudo", "systemctl", "status", f"wg-quick@{interface}"]).decode()
        for line in wg_status.splitlines():
            if "Active:" in line:
                logger.info(f"{WG_EMOJI} Status WireGuard: {line.strip()}")

        # Wyświetl status zapory
        firewall_status = subprocess.check_output(["sudo", "firewall-cmd", "--list-ports"]).decode()
        for line in firewall_status.splitlines():
            logger.info(f"{FIREWALL_EMOJI} Status zapory: {line.strip()}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Błąd restartowania WireGuard: {e}")
'''

def add_user_to_server_config(config_file, nickname, public_key, preshared_key, allowed_ips):
    with open(config_file, 'a') as file:
        file.write(f"\n### Klient {nickname}\n")
        file.write(f"[Peer]\n")
        file.write(f"PublicKey = {public_key}\n")
        file.write(f"PresharedKey = {preshared_key}\n")
        file.write(f"AllowedIPs = {allowed_ips}\n")

def generate_config(nickname, params, config_file, email="N/A", telegram_id="N/A"):
    """
    Generuje konfigurację użytkownika i kod QR.
    """
    logger.info("+--------- Proces 🌱 Tworzenie Użytkownika Uruchomione ---------+")
    try:
        logger.info(f"{INFO_EMOJI} Rozpoczynanie generowania konfiguracji dla użytkownika: {nickname}")
        
        # Sprawdź SERVER_PUB_IP
        server_public_key = params['SERVER_PUB_KEY']
        if not params.get('SERVER_PUB_IP'):
            raise ValueError("Brak parametru SERVER_PUB_IP. Sprawdź plik konfiguracyjny.")
        
        endpoint = f"{params['SERVER_PUB_IP']}:{params['SERVER_PORT']}"
        dns_servers = f"{params['CLIENT_DNS_1']},{params['CLIENT_DNS_2']}"

        private_key = generate_private_key()
        logger.debug(f"{DEBUG_EMOJI} Klucz prywatny pomyślnie wygenerowany.")
        public_key = generate_public_key(private_key)
        logger.debug(f"{DEBUG_EMOJI} Klucz publiczny pomyślnie wygenerowany.")
        preshared_key = generate_preshared_key()
        logger.debug(f"{DEBUG_EMOJI} Klucz współdzielony pomyślnie wygenerowany.")

        # Oblicz podsieć
        subnet = calculate_subnet(params.get('SERVER_WG_IPV4', '10.66.66.1'))
        logger.debug(f"{DEBUG_EMOJI} Używana podsieć: {subnet}")

        # Generuj adres IP
        new_ipv4 = generate_next_ip(config_file, subnet)
        logger.info(f"{INFO_EMOJI} Nowy adres IP użytkownika: {new_ipv4}")

        # Generuj konfigurację klienta
        client_config = create_client_config(
            private_key=private_key,
            address=new_ipv4,
            dns_servers=dns_servers,
            server_public_key=server_public_key,
            preshared_key=preshared_key,
            endpoint=endpoint
        )
        logger.debug(f"{DEBUG_EMOJI} Konfiguracja klienta pomyślnie utworzona.")

        config_path = os.path.join(settings.WG_CONFIG_DIR, f"{nickname}.conf")
        qr_path = os.path.join(settings.QR_CODE_DIR, f"{nickname}.png")

        # Zapisz konfigurację
        os.makedirs(settings.WG_CONFIG_DIR, exist_ok=True)
        with open(config_path, "w") as file:
            file.write(client_config)
        logger.info(f"{INFO_EMOJI} Konfiguracja użytkownika zapisana do {config_path}")

        # Generuj kod QR
        generate_qr_code(client_config, qr_path)

        # Dodaj użytkownika do konfiguracji serwera
        add_user_to_server_config(config_file, nickname, public_key.decode('utf-8'), preshared_key.decode('utf-8'), new_ipv4)
        logger.info(f"{INFO_EMOJI} Użytkownik pomyślnie dodany do konfiguracji serwera.")

        # Dodaj rekord użytkownika
        user_record = create_user_record(
            username=nickname,
            address=new_ipv4,
            public_key=public_key.decode('utf-8'),
            preshared_key=preshared_key.decode('utf-8'),
            qr_code_path=qr_path,
            email=email,
            telegram_id=telegram_id
        )
        logger.debug(f"{DEBUG_EMOJI} Rekord użytkownika utworzony.")

        # Zapisz do bazy danych
        user_records_path = os.path.join("user", "data", "user_records.json")
        os.makedirs(os.path.dirname(user_records_path), exist_ok=True)
        with open(user_records_path, "r+", encoding="utf-8") as file:
            try:
                user_data = json.load(file)
                logger.debug(f"{DEBUG_EMOJI} Wczytano istniejące rekordy użytkowników.")
            except json.JSONDecodeError:
                user_data = {}
                logger.warning(f"{WARNING_EMOJI} Błąd odczytu bazy użytkowników, zostanie utworzona nowa.")
            user_data[nickname] = user_record
            file.seek(0)
            json.dump(user_data, file, indent=4)
            file.truncate()
        logger.info(f"{INFO_EMOJI} Dane użytkownika {nickname} pomyślnie dodane do {user_records_path}")

        # Synchronizuj WireGuard
        params_path = "/etc/wireguard/params"
        if os.path.exists(params_path):
            with open(params_path, "r") as file:
                for line in file:
                    if line.startswith("SERVER_WG_NIC="):
                        server_wg_nic = line.strip().split("=")[1].strip('"')
                        break
                else:
                    raise ValueError("Nie znaleziono SERVER_WG_NIC w /etc/wireguard/params.")
        else:
            raise FileNotFoundError(f"Nie znaleziono pliku {params_path}.")

        sync_command = f'wg syncconf "{server_wg_nic}" <(wg-quick strip "{server_wg_nic}")'
        subprocess.run(sync_command, shell=True, check=True, executable='/bin/bash')
        logger.info(f"WireGuard zsynchronizowany dla interfejsu {server_wg_nic}")

        logger.info("+--------- Proces 🌱 Tworzenie Użytkownika Zakończone --------------+\n")
        return config_path, qr_path
    except Exception as e:
        logger.error(f"Błąd wykonania: {e}")
        logger.info("+--------- Proces 🌱 Tworzenie Użytkownika Zakończone --------------+\n")
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Za mało argumentów. Użycie: python3 main.py <nick> [email] [telegram_id]")
        sys.exit(1)

    nickname = sys.argv[1]
    email = sys.argv[2] if len(sys.argv) > 2 else "N/A"
    telegram_id = sys.argv[3] if len(sys.argv) > 3 else "N/A"
    params_file = settings.PARAMS_FILE

    logger.info("Rozpoczynanie procesu tworzenia użytkownika WireGuard.")
    try:
        logger.info("Inicjalizacja katalogów.")
        setup_directories()

        logger.info(f"Wczytywanie parametrów z pliku: {params_file}")
        params = load_params(params_file)

        logger.info("Sprawdzanie istniejącego użytkownika.")
        existing_users = load_existing_users()
        if nickname.lower() in existing_users:
            logger.error(f"Użytkownik o nazwie '{nickname}' już istnieje w bazie danych.")
            sys.exit(1)

        if is_user_in_server_config(nickname, settings.SERVER_CONFIG_FILE):
            logger.error(f"Użytkownik o nazwie '{nickname}' już istnieje w konfiguracji serwera.")
            sys.exit(1)

        logger.info("Generowanie konfiguracji użytkownika.")
        config_file = settings.SERVER_CONFIG_FILE
        config_path, qr_path = generate_config(nickname, params, config_file, email, telegram_id)

        logger.info(f"✅ Konfiguracja użytkownika zapisana do {config_path}")
        logger.info(f"✅ Kod QR użytkownika pomyślnie zapisany do {qr_path}")
    except FileNotFoundError as e:
        logger.error(f"Nie znaleziono pliku: {e}")
    except KeyError as e:
        logger.error(f"Brak klucza w parametrach: {e}")
    except ValueError as e:
        logger.error(f"Błąd wartości parametru: {e}")
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd: {e}")
