#!/usr/bin/env python3
# gradio_admin/functions/block_user.py

import json
import subprocess  # Do zarządzania VPN przez polecenia systemowe
from settings import USER_DB_PATH, SERVER_CONFIG_FILE  # Ścieżki do JSON i konfiguracji WireGuard
from settings import SERVER_WG_NIC

def load_user_records():
    """Wczytuje rekordy użytkowników z JSON."""
    try:
        with open(USER_DB_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"[BŁĄD] Nie udało się wczytać rekordów użytkowników: {e}")
        return {}

def save_user_records(records):
    """Zapisuje rekordy użytkowników do JSON."""
    try:
        with open(USER_DB_PATH, "w") as f:
            json.dump(records, f, indent=4)
        return True
    except Exception as e:
        print(f"[BŁĄD] Nie udało się zapisać rekordów użytkowników: {e}")
        return False

def block_user(username):
    """
    Blokuje użytkownika:
    1. Aktualizuje status w JSON na 'blocked'.
    2. Usuwa użytkownika z konfiguracji WireGuard.
    """
    records = load_user_records()
    if username not in records:
        return False, f"Użytkownik '{username}' nie znaleziony."

    # Aktualizuj status w JSON
    records[username]["status"] = "blocked"
    if not save_user_records(records):
        return False, f"Nie udało się zaktualizować JSON dla użytkownika '{username}'."

    # Usuń użytkownika z konfiguracji
    if not update_wireguard_config(username, block=True):
        return False, f"Nie udało się zablokować dostępu VPN dla użytkownika '{username}'."

    return True, f"Użytkownik '{username}' został zablokowany i dostęp VPN cofnięty."

def unblock_user(username):
    """
    Odblokowuje użytkownika:
    1. Aktualizuje status w JSON na 'active'.
    2. Przywraca użytkownika w konfiguracji WireGuard.
    """
    records = load_user_records()
    if username not in records:
        return False, f"Użytkownik '{username}' nie znaleziony."

    # Aktualizuj status w JSON
    records[username]["status"] = "active"
    if not save_user_records(records):
        return False, f"Nie udało się zaktualizować JSON dla użytkownika '{username}'."

    # Przywróć użytkownika w konfiguracji
    if not update_wireguard_config(username, block=False):
        return False, f"Nie udało się przywrócić dostępu VPN dla użytkownika '{username}'."

    return True, f"Użytkownik '{username}' został odblokowany i dostęp VPN przywrócony."

def update_wireguard_config(username, block=True):
    """
    Aktualizuje plik konfiguracji WireGuard:
    1. Jeśli block=True, komentuje cały blok [Peer] powiązany z użytkownikiem.
    2. Jeśli block=False, przywraca blok [Peer].
    """
    try:
        with open(SERVER_CONFIG_FILE, "r") as f:
            config_lines = f.readlines()

        updated_lines = []
        in_peer_block = False
        peer_belongs_to_user = False

        for idx, line in enumerate(config_lines):
            stripped_line = line.strip()

            # Identyfikuj użytkownika przez komentarz ### Client <username>
            if stripped_line == f"### Client {username}":
                in_peer_block = True
                peer_belongs_to_user = True
                updated_lines.append(line)  # Dodaj komentarz bez zmian
                continue

            # Przetwarzaj blok [Peer] jeśli należy do użytkownika
            if in_peer_block and peer_belongs_to_user:
                if block:
                    if not line.startswith("#"):
                        updated_lines.append(f"# {line}")  # Zakomentuj linię
                    else:
                        updated_lines.append(line)  # Już zakomentowane
                else:
                    if line.startswith("# "):
                        updated_lines.append(line[2:])  # Usuń komentarz
                    else:
                        updated_lines.append(line)  # Już odkomentowane

                # Koniec bloku [Peer] - pusta linia
                if stripped_line == "":
                    in_peer_block = False
                    peer_belongs_to_user = False
                continue

            # Wszystkie inne linie
            updated_lines.append(line)

        # Zapisz zaktualizowany plik konfiguracji
        with open(SERVER_CONFIG_FILE, "w") as f:
            f.writelines(updated_lines)

        # Zsynchronizuj WireGuard
        sync_command = f'wg syncconf "{SERVER_WG_NIC}" <(wg-quick strip "{SERVER_WG_NIC}")'
        subprocess.run(sync_command, shell=True, check=True, executable='/bin/bash')
        print(f"WireGuard zsynchronizowany dla interfejsu {SERVER_WG_NIC}")

        return True

    except Exception as e:
        print(f"[BŁĄD] Nie udało się zaktualizować konfiguracji WireGuard: {e}")
        return False
