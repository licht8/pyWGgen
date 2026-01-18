#!/usr/bin/env python3
# modules/traffic_updater.py

import json
import os
import subprocess
from settings import SERVER_WG_NIC  # Import interfejsu WireGuard z ustawień
from settings import USER_DB_PATH

def update_traffic_data(user_records_path):
    """
    Aktualizuje dane o ruchu użytkowników, zapisując te same wartości dla transfer i total_transfer w user_records.json.
    """
    if not os.path.exists(USER_DB_PATH):
        print(f"Plik {USER_DB_PATH} nie istnieje.")
        return

    # Wczytaj dane użytkowników
    with open(USER_DB_PATH, "r") as f:
        user_records = json.load(f)

    try:
        # Pobierz dane o ruchu z WireGuard
        output = subprocess.check_output(["wg", "show", SERVER_WG_NIC, "transfer"], text=True)
        lines = output.strip().split("\n")

        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                public_key = parts[0]
                received = int(parts[1])  # Aktualne odebrane dane
                sent = int(parts[2])

                # Znajdź użytkownika po kluczu publicznym
                for username, user_data in user_records.items():
                    if user_data.get("public_key") == public_key:
                        # Aktualizuj pole transfer
                        transfer_str = f"{received / (1024 ** 2):.2f} MiB odebrano, {sent / (1024 ** 2):.2f} MiB wysłano"
                        user_data["transfer"] = transfer_str
                        user_data["total_transfer"] = transfer_str  # Powtórz wartość
                        break

    except Exception as e:
        print(f"Błąd aktualizacji danych o ruchu: {e}")
        return

    # Zapisz zaktualizowane dane
    with open(USER_DB_PATH, "w") as f:
        json.dump(user_records, f, indent=4)
