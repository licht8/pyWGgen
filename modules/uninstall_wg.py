#!/usr/bin/env python3
# pyWGgen/modules/uninstall_wg.py
# ===========================================
# Skrypt do odinstalowywania WireGuard
# ===========================================

import os
import shutil
import subprocess
import platform
import logging
from pathlib import Path
from settings import PRINT_SPEED, LINE_DELAY

# Import ustawień projektu
try:
    from settings import (
        SERVER_CONFIG_FILE,
        PARAMS_FILE,
        WG_CONFIG_DIR,
        LOG_FILE_PATH,
        LOG_LEVEL,
        LOG_DIR,
    )
except ImportError:
    print("❌ Nie można zaimportować ustawień. Upewnij się, że skrypt jest uruchamiany z katalogu głównego projektu.")
    exit(1)

# Konfiguracja logowania
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=getattr(logging, LOG_LEVEL, "INFO"),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def uninstall_wireguard():
    local_print_speed = PRINT_SPEED  # Lokalna prędkość dla dostosowania
    """Funkcja do odinstalowywania WireGuard."""
    
    def confirm_action(prompt="Czy na pewno? (tak/nie): "):
        """Pyta użytkownika o potwierdzenie kontynuacji."""
        while True:
            choice = input(prompt).strip().lower()
            if choice in {"tak", "t", "yes", "y"}:
                return True
            elif choice in {"nie", "n", "no"}:
                return False
            print("⚠️  Nieprawidłowe dane. Wpisz 'tak' lub 'nie'.")

    def is_wireguard_installed():
        """Sprawdza czy WireGuard jest zainstalowany."""
        return shutil.which("wg") is not None

    def detect_package_manager():
        """Wykrywa menedżer pakietów na podstawie systemu operacyjnego."""
        distro = platform.system()
        if distro == "Linux":
            with open("/etc/os-release", "r") as f:
                os_release = f.read()
                if "Ubuntu" in os_release:
                    return "apt"
                elif "CentOS" in os_release or "Stream" in os_release:
                    return "dnf"
        print("❌ Nieobsługiwany system lub dystrybucja. Wyjście.")
        logger.error("Nieobsługiwany system lub dystrybucja.")
        exit(1)

    def stop_wireguard():
        """Zatrzymuje usługę WireGuard."""
        try:
            logger.info("Zatrzymywanie usługi WireGuard...")
            result = subprocess.run(["systemctl", "is-active", "--quiet", "wg-quick@wg0"])
            if result.returncode == 0:  # Usługa jest aktywna
                subprocess.run(["systemctl", "stop", "wg-quick@wg0"], check=True)
                logger.info("Usługa WireGuard zatrzymana.")
                print("✅ Usługa WireGuard zatrzymana.")
            else:
                logger.info("Usługa WireGuard nie jest aktywna lub już zatrzymana.")
                print("⚠️ Usługa WireGuard nie jest aktywna lub już zatrzymana.")
        except subprocess.CalledProcessError as e:
            logger.error("Nie udało się zatrzymać usługi WireGuard: %s", e)
            print("❌ Nie udało się zatrzymać usługi WireGuard. Sprawdź logi.")
            return False
        return True

    def remove_config_files():
        """Usuwa pliki konfiguracyjne WireGuard."""
        try:
            if SERVER_CONFIG_FILE.exists():
                SERVER_CONFIG_FILE.unlink()
                logger.info(f"Usunięto plik konfiguracji serwera: {SERVER_CONFIG_FILE}")
                print("✅ Usunięto plik konfiguracji serwera.")
            else:
                print("⚠️ Plik konfiguracji serwera nie znaleziony.")
                
            if PARAMS_FILE.exists():
                PARAMS_FILE.unlink()
                logger.info(f"Usunięto plik parametrów: {PARAMS_FILE}")
                print("✅ Usunięto plik parametrów.")
            else:
                print("⚠️ Plik parametrów nie znaleziony.")
                
            if WG_CONFIG_DIR.exists():
                shutil.rmtree(WG_CONFIG_DIR)
                logger.info(f"Usunięto katalog konfiguracji użytkowników WireGuard: {WG_CONFIG_DIR}")
                print("✅ Usunięto katalog konfiguracji WireGuard.")
            else:
                print("⚠️ Katalog konfiguracji WireGuard nie znaleziony.")
                
            print("✅ Pliki konfiguracyjne usunięte.")
        except Exception as e:
            logger.error("Nie udało się usunąć plików konfiguracyjnych: %s", e)
            print("❌ Nie udało się usunąć plików konfiguracyjnych. Sprawdź logi.")

    def remove_firewall_rules():
        """Usuwa reguły firewalla powiązane z WireGuard."""
        try:
            logger.info("Usuwanie reguł firewalla WireGuard...")
            if subprocess.run(["firewall-cmd", "--zone=public", "--remove-interface=wg0"], check=False).returncode != 0:
                print("⚠️ Interfejs firewalla 'wg0' nie znaleziony lub już usunięty.")
                logger.warning("Interfejs firewalla 'wg0' nie znaleziony lub już usunięty.")
            print("✅ Reguły firewalla usunięte.")
        except Exception as e:
            logger.error("Nie udało się usunąć reguł firewalla: %s", e)
            print("❌ Nie udało się usunąć reguł firewalla. Sprawdź logi.")

    # Główna logika odinstalowywania WireGuard
    if not is_wireguard_installed():
        print("❌ WireGuard nie jest zainstalowany. Wyjście.")
        return

    if not confirm_action("Czy na pewno chcesz odinstalować WireGuard? (tak/nie): "):
        print("❌ Odinstalowywanie anulowane.")
        return

    print("🔄 Rozpoczynanie procesu odinstalowywania...")
    stop_wireguard()
    remove_config_files()
    remove_firewall_rules()
    
    # Opcjonalnie: usuń pakiety WireGuard
    package_manager = detect_package_manager()
    print(f"💡 Aby całkowicie usunąć pakiety WireGuard, użyj: sudo {package_manager} remove wireguard-tools kmod-wireguard")
    
    print("\n✅ WireGuard został pomyślnie odinstalowany.")
    print("📝 Szczegóły w logach: " + str(LOG_FILE_PATH))

# Wywołaj funkcję jeśli skrypt jest uruchamiany bezpośrednio
if __name__ == "__main__":
    uninstall_wireguard()
