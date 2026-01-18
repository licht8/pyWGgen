#!/usr/bin/env python3
# pyWGgen/settings.py
# ===========================================
# Ustawienia projektu pyWGgen
# ===========================================
# Ten plik zawiera główne ustawienia projektu, w tym ścieżki plików,
# katalogi, konfiguracje i parametry globalne.
# Centralizuje wszystkie ważne zmienne aby uprościć utrzymanie projektu.
#
# Przykład użycia:
# ---------------------
# from settings import BASE_DIR, WG_CONFIG_DIR, GRADIO_PORT
# 
# print(f"Katalog główny projektu: {BASE_DIR}")
# print(f"Katalog konfiguracji WireGuard: {WG_CONFIG_DIR}")
# print(f"Port dla Gradio: {GRADIO_PORT}")
#
# WAŻNE: Wszystkie ścieżki i parametry powinny być określone względem BASE_DIR.
# ===========================================
# Logowanie:
# Moduł logging jest używany do zarządzania logami w projekcie.
# Możesz zmienić poziom logowania przez zmienną LOG_LEVEL:
# - DEBUG: Wyświetla wszystkie wiadomości, włączając informacje debugowania.
# - INFO: Główne akcje bez wiadomości debugowania.
# - WARNING: Tylko ostrzeżenia i błędy.
# - ERROR: Tylko błędy.
# Logi są zapisywane zarówno do konsoli jak i do pliku określonego w LOG_FILE_PATH.
#
# Wersja: 1.7 (2026-01-10) 6:39

from pathlib import Path
import os
import configparser

# Zdefiniuj ścieżkę główną do katalogu projektu
BASE_DIR = Path(__file__).resolve().parent  # Ścieżka do katalogu głównego pyWGgen
PROJECT_DIR = BASE_DIR  # Dla kompatybilności, PROJECT_DIR = BASE_DIR

# Ścieżki plików i katalogów
WG_CONFIG_DIR = BASE_DIR / "user/data/wg_configs"  # Ścieżka do konfiguracji WireGuard użytkowników
QR_CODE_DIR = BASE_DIR / "user/data/qrcodes"       # Ścieżka do zapisanych kodów QR
STALE_CONFIG_DIR = BASE_DIR / "user/data/usr_stale_config"  # Ścieżka do nieaktualnych konfiguracji użytkowników
USER_DB_PATH = BASE_DIR / "user/data/user_records.json"  # Baza danych użytkowników
#IP_DB_PATH = BASE_DIR / "user/data/ip_records.json"      # Baza danych adresów IP
SERVER_CONFIG_FILE = Path("/etc/wireguard/wg0.conf")     # Ścieżka do pliku konfiguracyjnego serwera WireGuard
SERVER_BACKUP_CONFIG_FILE = Path("/etc/wireguard/wg0.conf.bak") # Ścieżka do pliku kopii zapasowej konfiguracji serwera WireGuard
PARAMS_FILE = Path("/etc/wireguard/params")             # Ścieżka do pliku parametrów WireGuard

# Parametry WireGuard
DEFAULT_TRIAL_DAYS = 30  # Domyślna ważność konta w dniach
WIREGUARD_PORT = 51820   # Port serwera WireGuard (domyślny) zakres [1-65535]
DEFAULT_SUBNET = "10.66.66.0/24"
USER_SET_SUBNET = DEFAULT_SUBNET
DNS_WIREGUAED = "1.1.1.1, 1.0.0.1, 8.8.8.8"

# Ollama
OLLAMA_HOST = "http://10.99.0.2:11434"
MODEL_NAME = "qwen2.5:3b"

# Logi
AI_ASSISTANT_LOG_DIR = "ai_assistant/logs"

# WireGuard
IGNORE_INTERFACES = ["wg-mgmt"]
WG_PORT = "51820/udp"

# Firewalld
FIREWALLD_ZONES = ["public", "internal", "external", "home", "trusted", "work", "dmz", "wg"]

# AI Ustawienia
AI_TEMPERATURE = 0.1
AI_TIMEOUT = 120
CHAT_TEMPERATURE = 0.2
CHAT_TIMEOUT = 90

# Ustawienia logowania
LOG_DIR = BASE_DIR / "user/data/logs"  # Katalog do przechowywania logów
DIAGNOSTICS_LOG = LOG_DIR / "diagnostics.log"  # Plik logu diagnostycznego
SUMMARY_REPORT_PATH = LOG_DIR / "summary_report.txt"  # Plik do przechowywania raportów podsumowujących
LOG_FILE_PATH = LOG_DIR / "app.log"  # Plik logu aplikacji
LOG_LEVEL = "DEBUG"  # Poziom logowania: DEBUG, INFO, WARNING, ERROR

# Ścieżki dla raportów i bazy wiadomości
TEST_REPORT_PATH = BASE_DIR / "logs/test_report.txt"    # Ścieżka do raportu testów

# Dodatkowe ścieżki dla modułów i narzędzi
MODULES_DIR = BASE_DIR / "modules"            # Katalog zawierający moduły
# AI_DIAGNOSTICS_DIR = BASE_DIR / "ai_diagnostics"  # Katalog z plikami diagnostycznymi

# Port dla Gradio
GRADIO_PORT = 7860  # Port do uruchamiania interfejsu Gradio

# Ustawienia animacji i prędkości drukowania
ANIMATION_SPEED = 0.2  # Opóźnienie między iteracjami animacji (w sekundach)
# Przykłady:
# - 0.1: Przyspieszona animacja, odpowiednia dla krótkich wiadomości.
# - 0.2 (domyślnie): Standardowa prędkość, płynna animacja dla komfortowego odbioru.
# - 0.3: Nieco wolniejsza, jeszcze płynniejszy efekt.
# - 0.5: Wolna animacja, podkreśla ważność lub przyciąga uwagę.

PRINT_SPEED = 0.02  # Prędkość wyświetlania znaków (w sekundach)
# Przykłady:
# - 0.02 (domyślnie): Standardowa prędkość, imituje ręczne pisanie.
# - 0.01: Szybkie pisanie, prawie natychmiastowe.
# - 0.05: Wolne pisanie, tworzy efekt przemyślanego tekstu.

LINE_DELAY = 0.1  # Opóźnienie między liniami (w sekundach)
# Przykłady:
# - 0.1 (domyślnie): Płynne przejście między liniami.
# - 0.05: Szybkie przejście między liniami, skraca czas wyświetlania.
# - 0.2: Wolne przejście, przyciąga uwagę do nowej linii.

# Funkcja do odczytu SERVER_WG_NIC z pliku params
def get_server_wg_nic(params_file):
    """
    Wyodrębnia wartość SERVER_WG_NIC z pliku params.
    :param params_file: Ścieżka do pliku params
    :return: Wartość SERVER_WG_NIC
    """
    if not os.path.exists(params_file):
        raise FileNotFoundError(f"Nie znaleziono pliku {params_file}.")

    with open(params_file, "r") as f:
        for line in f:
            if line.startswith("SERVER_WG_NIC="):
                # Wyodrębnij wartość po "=" i usuń spacje
                return line.split("=")[1].strip()
    raise ValueError("Nie znaleziono SERVER_WG_NIC w pliku params.")

# Zdefiniuj SERVER_WG_NIC
try:
    SERVER_WG_NIC = get_server_wg_nic(PARAMS_FILE)
except (FileNotFoundError, ValueError) as e:
    SERVER_WG_NIC = None
    print(f"⚠️ Nie udało się wczytać SERVER_WG_NIC: {e}")

def check_paths():
    """Sprawdza istnienie plików i katalogów."""
    paths = {
        "BASE_DIR": BASE_DIR,
        "PROJECT_DIR": PROJECT_DIR,
        "WG_CONFIG_DIR": WG_CONFIG_DIR,
        "QR_CODE_DIR": QR_CODE_DIR,
        "USER_DB_PATH": USER_DB_PATH,
        #"IP_DB_PATH": IP_DB_PATH,
        "SERVER_CONFIG_FILE": SERVER_CONFIG_FILE,
        "PARAMS_FILE": PARAMS_FILE,
        "LOG_DIR": LOG_DIR,
        "DIAGNOSTICS_LOG": DIAGNOSTICS_LOG,
        "SUMMARY_REPORT_PATH": SUMMARY_REPORT_PATH,
        "TEST_REPORT_PATH": TEST_REPORT_PATH,
        "MODULES_DIR": MODULES_DIR,
    }
    status = []
    for name, path in paths.items():
        exists = " ✅  Dostępny" if path.exists() else " ❌  Brakuje"
        status.append(f"{name}: {exists} ({path})")
    return "\n".join(status)


if __name__ == "__main__":
    print(f"\n === 🛠️  Status projektu pyWGgen ===\n")
    print(f"  Katalog główny projektu: {BASE_DIR}")
    print(f"  Port Gradio: {GRADIO_PORT}")
    print(f"  Port WireGuard: {WIREGUARD_PORT}\n")
    print(f" === 📂  Sprawdzanie plików i katalogów ===\n")
    print(check_paths())
    print(f"\n")
