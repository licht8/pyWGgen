#!/usr/bin/env python3
# delete_user.py
# Skrypt do usuwania użytkowników w projekcie pyWGgen

import os
import subprocess
from datetime import datetime
from modules.utils import read_json, write_json, get_wireguard_config_path
from settings import WG_CONFIG_DIR, QR_CODE_DIR, SERVER_WG_NIC

# Funkcja logowania (podobna do log_debug)
def log_debug(message):
    """
    Prosta funkcja do wyświetlania komunikatów na konsoli z timestampem w milisekundach.
    :param message: Wiadomość do wyświetlenia.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]  # Zachowaj milisekundy
    print(f"{timestamp} - DEBUG    ℹ️  {message}")

def delete_user(username):
    """
    Usuwa użytkownika z konfiguracji WireGuard i powiązanych plików.
    :param username: Nazwa użytkownika do usunięcia.
    :return: Komunikat o wyniku operacji.
    """
    log_debug("---------- 🔥 Proces usuwania użytkownika uruchomiony ----------")

    base_dir = os.getcwd()
    user_records_path = os.path.join(base_dir, "user", "data", "user_records.json")
    wg_config_path = get_wireguard_config_path()

    log_debug(f"➡️ Rozpoczynam usuwanie użytkownika: '{username}'.")

    if not os.path.exists(user_records_path):
        log_debug(f"❌ Plik danych użytkowników nie znaleziony: {user_records_path}")
        log_debug("---------- 🔥 Proces usuwania użytkownika zakończony ---------------\n")
        return "❌ Błąd: Brak pliku danych użytkowników."

    try:
        # Wczytaj dane użytkowników
        user_data = read_json(user_records_path)
        log_debug(f"📂 Dane użytkowników pomyślnie wczytane.")

        if username not in user_data:
            log_debug(f"❌ Użytkownik '{username}' nie znaleziony w danych.")
            log_debug("---------- 🔥 Proces usuwania użytkownika zakończony ---------------\n")
            return f"❌ Użytkownik '{username}' nie istnieje."

        # Usuń rekord użytkownika z user_records.json
        user_info = user_data.pop(username)
        user_info["removed_at"] = datetime.now().isoformat()
        write_json(user_records_path, user_data)
        log_debug(f"📝 Rekord użytkownika '{username}' usunięty z danych.")

        # Usuń plik konfiguracyjny użytkownika
        wg_config_file = os.path.join(WG_CONFIG_DIR, f"{username}.conf")
        if os.path.exists(wg_config_file):
            os.remove(wg_config_file)
            log_debug(f"🗑️ Plik konfiguracji użytkownika '{wg_config_file}' usunięty.")

        # Usuń kod QR użytkownika
        qr_code_file = os.path.join(QR_CODE_DIR, f"{username}.png")
        if os.path.exists(qr_code_file):
            os.remove(qr_code_file)
            log_debug(f"🗑️ Kod QR użytkownika '{qr_code_file}' usunięty.")

        # Wyodrębnij klucz publiczny użytkownika
        public_key = extract_public_key(username, wg_config_path)
        if not public_key:
            log_debug(f"❌ Klucz publiczny użytkownika '{username}' nie znaleziony w konfiguracji WireGuard.")
            log_debug("---------- 🔥 Proces usuwania użytkownika zakończony ---------------\n")
            return f"❌ Brak klucza publicznego dla użytkownika '{username}'."

        # Usuń użytkownika z WireGuard
        subprocess.run(["sudo", "wg", "set", "wg0", "peer", public_key, "remove"], check=True)
        log_debug(f"🔐 Użytkownik '{username}' usunięty z WireGuard.")

        # Aktualizuj konfigurację WireGuard
        remove_peer_from_config(public_key, wg_config_path, username)
        log_debug(f"✅ Konfiguracja WireGuard pomyślnie zaktualizowana.")

        # Zsynchronizuj WireGuard
        sync_command = f'wg syncconf "{SERVER_WG_NIC}" <(wg-quick strip "{SERVER_WG_NIC}")'
        subprocess.run(sync_command, shell=True, check=True, executable='/bin/bash')
        print(f"WireGuard zsynchronizowany dla interfejsu {SERVER_WG_NIC}")

        log_debug("---------- 🔥 Proces usuwania użytkownika zakończony ---------------\n")
        return f"✅ Użytkownik '{username}' pomyślnie usunięty."
    except Exception as e:
        log_debug(f"⚠️ Błąd usuwania użytkownika '{username}': {str(e)}")
        log_debug("---------- 🔥 Proces usuwania użytkownika zakończony ---------------\n")
        return f"❌ Błąd usuwania użytkownika '{username}': {str(e)}"

def extract_public_key(username, config_path):
    """
    Wyodrębnia klucz publiczny użytkownika z konfiguracji WireGuard.
    :param username: Nazwa użytkownika.
    :param config_path: Ścieżka do pliku konfiguracji WireGuard.
    :return: Klucz publiczny użytkownika.
    """
    log_debug(f"🔍 Wyszukiwanie klucza publicznego dla użytkownika '{username}' w {config_path}.")
    try:
        with open(config_path, "r") as f:
            lines = f.readlines()

        found_username = False
        for line in lines:
            if username in line:
                found_username = True
            elif found_username and line.strip().startswith("PublicKey"):
                public_key = line.split("=", 1)[1].strip()
                log_debug(f"🔑 Znaleziono klucz publiczny dla '{username}': {public_key}")
                return public_key
        log_debug(f"❌ Klucz publiczny dla '{username}' nie znaleziony.")
        return None
    except Exception as e:
        log_debug(f"⚠️ Błąd wyszukiwania klucza publicznego: {str(e)}")
        return None

def remove_peer_from_config(public_key, config_path, client_name):
    """
    Usuwa blok [Peer] i powiązany komentarz z pliku konfiguracji WireGuard.
    Usuwa komentarz i 4 kolejne linie od niego.
    :param public_key: Klucz publiczny użytkownika.
    :param config_path: Ścieżka do pliku konfiguracji WireGuard.
    :param client_name: Nazwa klienta.
    """
    log_debug(f"🛠️ Usuwanie konfiguracji użytkownika '{client_name}' z {config_path}.")

    try:
        with open(config_path, "r") as f:
            lines = f.readlines()

        updated_lines = []
        skip_lines = 0  # Licznik pomijanych linii

        for i, line in enumerate(lines):
            # Jeśli znaleziono komentarz klienta
            if line.strip() == f"### Client {client_name}":
                log_debug(f"📌 Znaleziono blok dla '{client_name}' w linii {i}. Usuwanie...")
                skip_lines = 5  # Pomiń 5 linii od tego miejsca
                continue

            # Pomiń linie związane z usuwanym blokiem
            if skip_lines > 0:
                log_debug(f"⏩ Pomijam linię {i}: {line.strip()}")
                skip_lines -= 1
                continue

            # Zapisz pozostałe linie
            updated_lines.append(line)

        # Zapisz zaktualizowaną konfigurację
        with open(config_path, "w") as f:
            f.writelines(updated_lines)

        log_debug(f"✅ Konfiguracja użytkownika '{client_name}' usunięta.")
    except Exception as e:
        log_debug(f"⚠️ Błąd aktualizacji konfiguracji: {str(e)}")
