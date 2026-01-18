#!/usr/bin/env python3
# modules/handshake_updater.py

import os
import json
import subprocess
from datetime import datetime
from settings import USER_DB_PATH, SERVER_WG_NIC

def get_latest_handshakes(interface):
    """
    Pobiera informacje o najnowszych handshake'ach użytkowników WireGuard.
    :param interface: Nazwa interfejsu WireGuard.
    :return: Słownik {klucz_publiczny: ostatni_handshake}.
    """
    try:
        output = subprocess.check_output(["wg", "show", interface, "latest-handshakes"], text=True)
        lines = output.strip().split("\n")
        handshakes = {}

        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                public_key = parts[0]
                timestamp = int(parts[1])
                handshakes[public_key] = convert_handshake_timestamp(timestamp)

        return handshakes
    except Exception as e:
        print(f"Błąd pobierania informacji o handshake'ach: {e}")
        return {}

def convert_handshake_timestamp(timestamp):
    """
    Konwertuje znacznik czasu Unix na czytelny format.
    :param timestamp: Znacznik czasu (Unix timestamp).
    :return: Czytelny ciąg daty i czasu w formacie UTC lub 'Nigdy' jeśli nie było handshake'a (timestamp = 0).
    """
    if timestamp == 0:
        return "Nigdy"
    return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")

def update_handshakes(user_records_path, interface):
    """
    Aktualizuje informacje o najnowszych handshake'ach użytkowników w user_records.json.
    :param user_records_path: Ścieżka do pliku user_records.json.
    :param interface: Nazwa interfejsu WireGuard.
    """
    if not os.path.exists(user_records_path):
        print(f"Plik {user_records_path} nie istnieje.")
        return

    with open(user_records_path, "r") as f:
        user_records = json.load(f)

    handshakes = get_latest_handshakes(interface)

    for username, user_data in user_records.items():
        public_key = user_data.get("public_key")
        if public_key in handshakes:
            user_data["last_handshake"] = handshakes[public_key]

    with open(user_records_path, "w") as f:
        json.dump(user_records, f, indent=4)

    print("Informacje o najnowszych handshake'ach pomyślnie zaktualizowane.")

if __name__ == "__main__":
    # Aktualizacja handshake'ów dla użytkowników
    update_handshakes(USER_DB_PATH, SERVER_WG_NIC)
