#!/usr/bin/env python3
# modules/manage_users_menu.py
# Moduł do zarządzania użytkownikami WireGuard
# Aktualizacja: 14/01/25

import os
import json
import sys
import subprocess
from modules.utils import get_wireguard_subnet, read_json, write_json
from settings import USER_DB_PATH, SERVER_CONFIG_FILE, WG_CONFIG_DIR, QR_CODE_DIR, SERVER_WG_NIC
from modules.traffic_updater import update_traffic_data
from modules.handshake_updater import update_handshakes

def ensure_directory_exists(filepath):
    """Zapewnia istnienie katalogu dla pliku."""
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_user_records():
    """Wczytuje dane użytkowników z pliku JSON."""
    return read_json(USER_DB_PATH)

def create_user():
    """Tworzy nowego użytkownika wywołując main.py."""
    username = input("Wprowadź nazwę użytkownika: ").strip()
    if not username:
        print("❌ Nazwa użytkownika nie może być pusta.")
        return

    email = input("Wprowadź email (opcjonalnie): ").strip() or "N/A"
    telegram_id = input("Wprowadź ID Telegram (opcjonalnie): ").strip() or "N/A"

    try:
        subprocess.run(
            ["python3", os.path.join("main.py"), username, email, telegram_id],
            check=True,
            cwd=os.path.abspath(os.path.dirname(__file__) + "/../")
        )

    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd tworzenia użytkownika: {e}")

def list_users():
    """Wyświetla listę wszystkich użytkowników."""
    records = load_user_records()
    if not records:
        print("⚠️ Lista użytkowników jest pusta.")
        return

    print("\n👤 Użytkownicy WireGuard:")
    for username, data in records.items():
        allowed_ips = data.get("allowed_ips", "N/A")
        status = data.get("status", "N/A")
        print(f"  - {username}: {allowed_ips} | Status: {status}")

def show_traffic():
    """Pobiera i wyświetla ruch użytkowników."""
    try:
        print("\n🔄 Aktualizacja ruchu użytkowników...")
        update_traffic_data(USER_DB_PATH)
        print("✅ Ruch użytkowników zaktualizowany.")

        records = load_user_records()
        print("\n📊 Ruch użytkowników:")
        for username, data in records.items():
            transfer = data.get("transfer", "N/A")
            total_transfer = data.get("total_transfer", "N/A")
            print(f"  - {username}: {transfer} | Razem: {total_transfer}")
    except Exception as e:
        print(f"⚠️ Błąd pobierania ruchu użytkowników: {e}")

def show_handshakes():
    """Pobiera i wyświetla informacje o ostatnich handshake'ach."""
    try:
        print("\n🔄 Aktualizacja informacji o ostatnich handshake'ach...")
        update_handshakes(USER_DB_PATH, SERVER_WG_NIC)
        print("✅ Informacje o ostatnich handshake'ach zaktualizowane.")

        records = load_user_records()
        print("\n🤝 Ostatnie handshake'i:")
        for username, data in records.items():
            last_handshake = data.get("last_handshake", "Nigdy")
            print(f"  - {username}: Ostatni handshake: {last_handshake}")
    except Exception as e:
        print(f"⚠️ Błąd aktualizacji informacji o handshake'ach: {e}")

def delete_user():
    """
    Usuwa użytkownika z konfiguracji WireGuard i powiązanych plików.
    """
    username = input("Wprowadź nazwę użytkownika do usunięcia: ").strip()
    if not username:
        print("❌ Błąd: Nazwa użytkownika nie może być pusta.")
        return

    print(f"➡️ Rozpoczynanie usuwania użytkownika: '{username}'.")

    if not os.path.exists(USER_DB_PATH):
        print(f"❌ Plik danych użytkowników nie znaleziony: {USER_DB_PATH}")
        return

    try:
        # Wczytaj dane użytkownika
        user_data = read_json(USER_DB_PATH)
        if username not in user_data:
            print(f"❌ Użytkownik '{username}' nie istnieje.")
            return

        # Usuń rekord użytkownika
        user_data.pop(username)
        write_json(USER_DB_PATH, user_data)
        print(f"📝 Rekord użytkownika '{username}' usunięty z danych.")

        # Usuń plik konfiguracyjny użytkownika
        wg_config_path = WG_CONFIG_DIR / f"{username}.conf"
        if wg_config_path.exists():
            wg_config_path.unlink()
            print(f"🗑️ Konfiguracja '{wg_config_path}' usunięta.")

        # Usuń kod QR użytkownika
        qr_code_path = QR_CODE_DIR / f"{username}.png"
        if qr_code_path.exists():
            qr_code_path.unlink()
            print(f"🗑️ Kod QR '{qr_code_path}' usunięty.")

        # Wyodrębnij klucz publiczny użytkownika
        public_key = extract_public_key(username, SERVER_CONFIG_FILE)
        if not public_key:
            print(f"❌ Klucz publiczny użytkownika '{username}' nie znaleziony w konfiguracji WireGuard.")
            return

        # Usuń użytkownika z WireGuard
        subprocess.run(["sudo", "wg", "set", "wg0", "peer", public_key, "remove"], check=True)
        print(f"🔐 Użytkownik '{username}' usunięty z WireGuard.")

        # Aktualizuj konfigurację WireGuard
        remove_peer_from_config(public_key, SERVER_CONFIG_FILE, username)
        print(f"✅ Konfiguracja WireGuard zaktualizowana.")

        # Zsynchronizuj WireGuard
        sync_command = f'wg syncconf "{SERVER_WG_NIC}" <(wg-quick strip "{SERVER_WG_NIC}")'
        subprocess.run(sync_command, shell=True, check=True, executable='/bin/bash')
        print(f"WireGuard zsynchronizowany dla interfejsu {SERVER_WG_NIC}")

        print(f"✅ Użytkownik '{username}' pomyślnie usunięty.")
    except Exception as e:
        print(f"⚠️ Błąd usuwania użytkownika '{username}': {e}")

def extract_public_key(username, config_path):
    """
    Wyodrębnia klucz publiczny użytkownika z pliku konfiguracyjnego WireGuard.

    Args:
        username (str): Nazwa użytkownika.
        config_path (str): Ścieżka do pliku konfiguracyjnego WireGuard.

    Returns:
        str: Klucz publiczny użytkownika.
    """
    try:
        with open(config_path, "r") as f:
            lines = f.readlines()

        found_username = False
        for line in lines:
            if username in line:
                found_username = True
            elif found_username and line.strip().startswith("PublicKey"):
                return line.split("=", 1)[1].strip()
        return None
    except Exception as e:
        print(f"⚠️ Błąd znajdowania klucza publicznego: {e}")
        return None

def remove_peer_from_config(public_key, config_path, client_name):
    """
    Usuwa sekcję [Peer] i powiązany komentarz z pliku konfiguracyjnego WireGuard.

    Args:
        public_key (str): Klucz publiczny użytkownika.
        config_path (str): Ścieżka do pliku konfiguracyjnego WireGuard.
        client_name (str): Nazwa klienta.
    """
    try:
        with open(config_path, "r") as f:
            lines = f.readlines()

        updated_lines = []
        skip_lines = 0

        for line in lines:
            # Jeśli znaleziono komentarz klienta
            if line.strip() == f"### Klient {client_name}":
                skip_lines = 5  # Usuń 5 linii zaczynając od tej
                continue

            # Pomiń linie związane z usuwanym blokiem
            if skip_lines > 0:
                skip_lines -= 1
                continue

            # Zachowaj inne linie
            updated_lines.append(line)

        # Zapisz zaktualizowaną konfigurację
        with open(config_path, "w") as f:
            f.writelines(updated_lines)
    except Exception as e:
        print(f"⚠️ Błąd aktualizacji konfiguracji: {e}")

def manage_users_menu():
    """Menu zarządzania użytkownikami."""
    while True:
        print("\n========== Zarządzanie użytkownikami ==========")
        print("1. 🌱 Utwórz użytkownika")
        print("2. 🔍 Lista wszystkich użytkowników")
        print("3. ❌ Usuń użytkownika")
        print("4. 📊 Zobacz ruch użytkowników")
        print("5. 🤝 Zobacz ostatnie handshake'i")
        print("0. Powrót do menu głównego")
        print("===============================================")

        choice = input("Wybierz akcję: ").strip()
        if choice == "1":
            create_user()
        elif choice == "2":
            list_users()
        elif choice == "3":
            delete_user()
        elif choice == "4":
            show_traffic()
        elif choice == "5":
            show_handshakes()
        elif choice in {"0", "q"}:
            break
        else:
            print("⚠️ Nieprawidłowy wybór. Spróbuj ponownie.")
