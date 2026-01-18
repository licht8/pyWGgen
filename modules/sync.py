#!/usr/bin/env python3

import json
import shutil
from pathlib import Path
from settings import USER_DB_PATH, SERVER_CONFIG_FILE
from modules.main_registration_fields import create_user_record
from modules.qr_generator import generate_qr_code

def get_valid_path(prompt):
    """Pobiera poprawną ścieżkę do katalogu."""
    while True:
        path_str = input(prompt).strip()
        path = Path(path_str)
        if path.exists() and path.is_dir():
            return path
        print(f"Błąd: Katalog '{path_str}' nie istnieje. Spróbuj ponownie.\n")

def find_user_files(username, config_dir, qr_dir):
    """Znajduje pliki konfiguracyjne i QR użytkownika."""
    config_path = next(
        (f for ext in ['.conf', '.txt'] 
         if (f := config_dir / f"{username}{ext}").exists()),
        None
    )
    qr_path = next(
        (f for ext in ['.png', '.jpg', '.svg']
         if (f := qr_dir / f"{username}{ext}").exists()),
        None
    )
    return config_path, qr_path

def sync_users_from_config_paths(config_dir_str: str, qr_dir_str: str):
    """Synchronizuje użytkowników z plików konfiguracyjnych i QR."""
    logs = []
    try:
        config_dir = Path(config_dir_str)
        qr_dir = Path(qr_dir_str)

        if not config_dir.is_dir():
            raise ValueError(f"Katalog konfiguracji nie znaleziony: {config_dir}")
        if not qr_dir.is_dir():
            raise ValueError(f"Katalog kodów QR nie znaleziony: {qr_dir}")

        logs.append("=== 🛠 Rozpoczynanie synchronizacji użytkowników ===")
        logs.append(f"Katalog konfiguracji: {config_dir}\nKatalog QR: {qr_dir}\n")

        # Parsowanie konfiguracji serwera
        with open(SERVER_CONFIG_FILE, "r") as f:
            config_content = f.read()

        users = []
        current_user = {}
        for line in config_content.split('\n'):
            line = line.strip()
            if line.startswith("### Client"):
                if current_user:
                    users.append(current_user)
                current_user = {"username": line.split("### Client")[1].strip()}
            elif line.startswith("PublicKey ="):
                _, value = line.split('=', 1)
                public_key = value.strip()
                missing_padding = len(public_key) % 4
                if missing_padding:
                    public_key += '=' * (4 - missing_padding)
                current_user["public_key"] = public_key
            elif line.startswith("PresharedKey ="):
                _, value = line.split('=', 1)
                preshared_key = value.strip()
                missing_padding = len(preshared_key) % 4
                if missing_padding:
                    preshared_key += '=' * (4 - missing_padding)
                current_user["preshared_key"] = preshared_key
            elif line.startswith("AllowedIPs ="):
                current_user["allowed_ips"] = line.split('=', 1)[1].strip()
            elif line == "" and current_user:
                users.append(current_user)
                current_user = {}
        if current_user:
            users.append(current_user)

        # Wczytaj istniejące rekordy
        user_records = {}
        if USER_DB_PATH.exists():
            with open(USER_DB_PATH, "r") as f:
                user_records = json.load(f)

        new_users = 0
        for user in users:
            username = user["username"]
            logs.append(f"Przetwarzanie: {username}")

            config_path, qr_path = find_user_files(username, config_dir, qr_dir)
            
            # Pomiń jeśli brak plików
            if not config_path and not qr_path:
                logs.append(f"  ❗ Pomijanie - brak konfiguracji/QR")
                continue

            target_config = Path(f"user/data/wg_configs/{username}.conf")
            target_qr = Path(f"user/data/qrcodes/{username}.png")
            
            # Utwórz katalogi jeśli potrzeba
            target_config.parent.mkdir(parents=True, exist_ok=True)
            target_qr.parent.mkdir(parents=True, exist_ok=True)

            # Obsługa pliku konfiguracyjnego
            config_processed = False
            if config_path:
                shutil.copy(config_path, target_config)
                logs.append(f"  ✅ Skopiowano konfigurację: {config_path.name}")
                config_processed = True
            else:
                logs.append(f"  ⚠️ Brak pliku konfiguracyjnego")

            # Obsługa kodu QR
            qr_processed = False
            if qr_path:
                shutil.copy(qr_path, target_qr)
                logs.append(f"  ✅ Skopiowano QR: {qr_path.name}")
                qr_processed = True
            elif config_processed:
                try:
                    generate_qr_code(target_config.read_text(), str(target_qr))
                    logs.append("  🔄 Wygenerowano QR z konfiguracji")
                    qr_processed = True
                except Exception as e:
                    logs.append(f"  ❗ Błąd generowania QR: {str(e)}")

            # Pomiń jeśli brak przetworzonych plików
            if not config_processed and not qr_processed:
                logs.append(f"  ❗ Pomijanie - brak przetworzonych plików")
                continue

            # Aktualizuj rekordy użytkowników
            if username not in user_records:
                user_record = create_user_record(
                    username=username,
                    address=user.get("allowed_ips", ""),
                    public_key=user.get("public_key", ""),
                    preshared_key=user.get("preshared_key", ""),
                    qr_code_path=str(target_qr) if qr_processed else None
                )
                user_record["config_path"] = str(target_config) if config_processed else None
                user_records[username] = user_record
                new_users += 1

        # Zapisz zaktualizowaną bazę
        with open(USER_DB_PATH, "w") as f:
            json.dump(user_records, f, indent=4)

        logs.append(f"\n✅ Synchronizacja zakończona! Nowi użytkownicy: {new_users}")
        return True, "\n".join(logs)

    except Exception as e:
        logs.append(f"❌ Krytyczny błąd: {str(e)}")
        return False, "\n".join(logs)

def sync_users_from_config():
    """Synchronizacja użytkowników w trybie konsolowym."""
    try:
        print("\n=== 🔄 Synchronizacja użytkowników (tryb konsolowy) ===")
        config_dir = get_valid_path("Ścieżka do konfiguracji klientów: ")
        qr_dir = get_valid_path("Ścieżka do kodów QR: ")
        
        success, log = sync_users_from_config_paths(str(config_dir), str(qr_dir))
        print(log)
        return success
        
    except KeyboardInterrupt:
        print("\n🚫 Operacja anulowana przez użytkownika")
        return False

if __name__ == "__main__":
    sync_users_from_config()
