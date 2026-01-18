#!/usr/bin/env python3
# utils.py
# Funkcje pomocnicze dla projektu wg_qr_generator.

import json
import os
import datetime

def read_json(file_path):
    """
    Wczytuje dane z pliku JSON.
    :param file_path: Ścieżka do pliku JSON.
    :return: Zawartość pliku jako słownik.
    """
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json(file_path, data):
    """
    Zapisuje dane do pliku JSON.
    :param file_path: Ścieżka do pliku JSON.
    :param data: Dane do zapisania.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def get_wireguard_config_path():
    """
    Pobiera ścieżkę do aktualnego pliku konfiguracji WireGuard.
    :return: Ścieżka do pliku konfiguracji.
    """
    return "/etc/wireguard/wg0.conf"

def parse_wireguard_config(config_path=None):
    """
    Odczytuje i parsuje plik konfiguracji WireGuard.
    :param config_path: Ścieżka do pliku konfiguracji.
    :return: Zawartość pliku jako ciąg znaków.
    """
    if config_path is None:
        config_path = get_wireguard_config_path()

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Nie znaleziono pliku konfiguracji WireGuard: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as file:
        return file.read()

def get_wireguard_subnet(config_path=None):
    """
    Wyodrębnia podsieć WireGuard z pliku konfiguracji.
    :param config_path: Ścieżka do pliku konfiguracji.
    :return: Podsieć jako ciąg znaków (np. "10.66.66.1/24").
    """
    if config_path is None:
        config_path = get_wireguard_config_path()

    config_content = parse_wireguard_config(config_path)
    for line in config_content.splitlines():
        if line.strip().startswith("Address"):
            addresses = line.split('=')[1].strip().split(',')
            for address in addresses:
                if '/' in address and '.' in address:  # IPv4
                    return address.strip()
    raise ValueError(f"Nie udało się znaleźć podsieci WireGuard w pliku konfiguracji {config_path}.")

def log_debug(message):
    """
    Loguje wiadomości debugowania.
    :param message: Wiadomość do zalogowania.
    """
    timestamp = datetime.datetime.now().isoformat()
    log_file_path = "debug.log"
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"[DEBUG] {timestamp} - {message}\n")
    print(f"[DEBUG] {timestamp} - {message}")
