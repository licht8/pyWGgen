#!/usr/bin/env python3
# modules/user_data_cleaner.py
# Moduł do selektywnego czyszczenia danych użytkowników

import os
import shutil
import subprocess
from settings import SERVER_WG_NIC  # SERVER_WG_NIC z pliku parametrów
from settings import USER_DB_PATH  # Baza danych użytkowników
from settings import SERVER_CONFIG_FILE
from settings import SERVER_BACKUP_CONFIG_FILE
from settings import WG_CONFIG_DIR, QR_CODE_DIR

WG_USERS_JSON = "logs/wg_users.json"

def confirm_action(message):
    """Potwierdzenie użytkownika dla akcji."""
    while True:
        choice = input(f"{message} (t/n): ").strip().lower()
        if choice in {"t", "y", "tak", "yes"}:
            return True
        elif choice in {"n", "nie", "no"}:
            return False
        print("⚠️ Wpisz 't' aby potwierdzić lub 'n' aby anulować.")

def clean_user_data():
    """Selektywne czyszczenie danych użytkowników z potwierdzeniem."""
    try:
        # Czyszczenie user_records.json
        if os.path.exists(USER_DB_PATH) and confirm_action("🧹 Wyczyścić plik user_records.json?"):
            os.remove(USER_DB_PATH)
            print(f"✅ {USER_DB_PATH} wyczyszczony.")

        # Czyszczenie wg_users.json
        if os.path.exists(WG_USERS_JSON) and confirm_action("🧹 Wyczyścić plik wg_users.json?"):
            os.remove(WG_USERS_JSON)
            print(f"✅ {WG_USERS_JSON} wyczyszczony.")

        # Czyszczenie konfiguracji WireGuard
        if os.path.exists(SERVER_CONFIG_FILE) and confirm_action("🧹 Wyczyścić plik konfiguracji WireGuard (usunąć wszystkie ### Client i [Peer])?"):
            # Utwórz kopię zapasową
            shutil.copy2(SERVER_CONFIG_FILE, SERVER_BACKUP_CONFIG_FILE)
            print(f"✅ Utworzono kopię zapasową: {SERVER_BACKUP_CONFIG_FILE}")

            # Wyczyść konfigurację
            with open(SERVER_CONFIG_FILE, "r") as wg_file:
                lines = wg_file.readlines()

            # Nowa zawartość bez bloków ### Client i powiązanych [Peer]
            cleaned_lines = []
            inside_client_block = False

            for line in lines:
                stripped_line = line.strip()
                if stripped_line.startswith("### Client"):
                    inside_client_block = True
                elif inside_client_block and stripped_line == "":
                    # Koniec bloku, przełącz flagę
                    inside_client_block = False
                elif not inside_client_block:
                    cleaned_lines.append(line)

            with open(SERVER_CONFIG_FILE, "w") as wg_file:
                wg_file.writelines(cleaned_lines)
            print(f"✅ Konfiguracja WireGuard wyczyszczona.")

        # Czyszczenie plików konfiguracyjnych użytkowników
        if os.path.exists(WG_CONFIG_DIR) and confirm_action("🧹 Wyczyścić wszystkie pliki konfiguracyjne użytkowników?"):
            for config_file in os.listdir(WG_CONFIG_DIR):
                file_path = os.path.join(WG_CONFIG_DIR, config_file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print(f"✅ Pliki konfiguracyjne użytkowników w {WG_CONFIG_DIR} wyczyszczone.")

        # Czyszczenie kodów QR użytkowników
        if os.path.exists(QR_CODE_DIR) and confirm_action("🧹 Wyczyścić wszystkie kody QR użytkowników?"):
            for qr_code_file in os.listdir(QR_CODE_DIR):
                file_path = os.path.join(QR_CODE_DIR, qr_code_file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print(f"✅ Kody QR użytkowników w {QR_CODE_DIR} wyczyszczone.")

        # Synchronizacja WireGuard
        sync_command = f'wg syncconf "{SERVER_WG_NIC}" <(wg-quick strip "{SERVER_WG_NIC}")'
        subprocess.run(sync_command, shell=True, check=True, executable='/bin/bash')
        print(f"WireGuard zsynchronizowany dla interfejsu {SERVER_WG_NIC}")

        print("🎉 Czyszczenie zakończone. Wszystkie dane przetworzone.")

    except Exception as e:
        print(f"❌ Błąd podczas czyszczenia danych: {e}")

if __name__ == "__main__":
    clean_user_data()
