#!/usr/bin/env python3
# ai_diagnostics/ai_diagnostics_summary.py
# Skrypt do generowania raportu podsumowującego stan projektu pyWGgen.
# Wersja: 1.7
# Zaktualizowano: 2024-12-02

import json
import subprocess
from pathlib import Path
import sys
import logging
import time

# Dodaj katalog główny projektu do sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))  # Dodaj katalog główny projektu do sys.path

# Importuj ustawienia
from settings import PROJECT_DIR, SUMMARY_REPORT_PATH, USER_DB_PATH, LOG_LEVEL

# Konfiguracja logowania
logging.basicConfig(
    level=logging.getLevelName(LOG_LEVEL),  # Użyj poziomu logowania z ustawień
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("diagnostics_summary.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def run_command(command):
    """Wykonuje polecenie w terminalu i zwraca wynik."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Błąd wykonywania polecenia {command}: {e.stderr.strip()}")
        return f"Błąd: {e.stderr.strip()}"


def check_ports():
    """Sprawdza otwarte porty."""
    command = ["ss", "-tuln"]
    result = run_command(command)
    open_ports = []
    if not result:
        logger.warning("Nie udało się pobrać listy otwartych portów.")
        return open_ports

    for line in result.splitlines():
        if ":51820" in line:
            open_ports.append("51820 (WireGuard)")
        if ":7860" in line:
            open_ports.append("7860 (Gradio)")
    logger.debug(f"Otwarte porty: {open_ports}")
    return open_ports


def check_firewall():
    """Sprawdza status zapory ogniowej i otwarte porty."""
    command_status = ["firewall-cmd", "--state"]
    command_ports = ["firewall-cmd", "--list-ports"]
    status = run_command(command_status)
    if status != "running":
        logger.warning(f"Zapora ogniowa nieaktywna: {status}")
        return f"Zapora ogniowa: {status}", []
    open_ports = run_command(command_ports).split()
    logger.debug(f"Otwarte porty zapory: {open_ports}")
    return f"Zapora ogniowa: Aktywna", open_ports


def check_wireguard_status():
    """Sprawdza czy usługa WireGuard jest aktywna."""
    command_status = ["sudo", "systemctl", "is-active", "wg-quick@wg0"]
    command_info = ["sudo", "wg", "show"]
    status = run_command(command_status)
    logger.debug(f"Status WireGuard: {status}")

    if status == "active":
        wg_info = run_command(command_info)
        logger.debug(f"Informacje WireGuard:\n{wg_info}")
        return status, wg_info
    return status, "WireGuard nieaktywny"


def count_users():
    """Zlicza liczbę użytkowników z pliku user_records.json."""
    if USER_DB_PATH.exists():
        try:
            with open(USER_DB_PATH, "r", encoding="utf-8") as file:
                user_data = json.load(file)
                user_count = len(user_data)
                logger.debug(f"Wykryto użytkowników: {user_count}")
                return user_count, "user_records.json"
        except json.JSONDecodeError:
            logger.error("Błąd odczytu pliku user_records.json.")
            return 0, "Błąd odczytu user_records.json"
    logger.warning("Brak pliku user_records.json.")
    return 0, "Brak pliku user_records.json"


def count_peers(wg_info):
    """Zlicza liczbę peerów z wyniku wg show."""
    if not wg_info:
        logger.warning("Informacje WireGuard niedostępne.")
        return 0
    peer_count = sum(1 for line in wg_info.splitlines() if line.startswith("peer:"))
    logger.debug(f"Liczba peerów: {peer_count}")
    return peer_count


def generate_summary():
    """Generuje raport podsumowujący stan projektu pyWGgen."""
    logger.info("Rozpoczęcie generowania raportu podsumowującego.")

    # Pobierz dane użytkowników
    total_users, user_source = count_users()

    # Sprawdź status WireGuard
    wg_status, wg_info = check_wireguard_status()
    peers_count = count_peers(wg_info) if wg_status == "active" else 0

    # Sprawdź porty
    open_ports = check_ports()

    # Sprawdź status zapory ogniowej
    firewall_status, firewall_ports = check_firewall()

    # Utwórz raport
    summary = [
        " 📂 Użytkownicy:",
        f"- Łącznie użytkowników: {total_users} (Źródło: {user_source})",
        "\n 🔒 WireGuard:",
        f" - Łącznie peerów: {peers_count} (Źródło: wg show)",
        f" - Status WireGuard: {wg_status}",
        f" - Informacje WireGuard:\n{wg_info if wg_status == 'active' else ''}",
        "\n 🌐 Gradio:",
        f" - Status: {'Nie działa' if '7860 (Gradio)' not in open_ports else 'Działa'}",
        "   - Aby uruchomić:",
        f"    1️⃣  Przejdź do katalogu głównego projektu:",
        "    2️⃣  Wykonaj \"🌐 Otwórz Panel Admina Gradio\"",
        "\n 🔥 Zapora ogniowa:",
        f" - {firewall_status}",
        " - Otwarte porty:",
        f"  - {', '.join(firewall_ports) if firewall_ports else 'Brak otwartych portów'}",
        "\n 🎯 Zalecenia:",
        " - Upewnij się, że liczba peerów odpowiada liczbie użytkowników.",
        " - Jeśli Gradio nie działa, postępuj według sugerowanych kroków.",
        " - Sprawdź, czy porty dla Gradio i WireGuard są dostępne przez zaporę ogniową.\n\n"
    ]

    # Zapisz raport
    try:
        with open(SUMMARY_REPORT_PATH, "w", encoding="utf-8") as file:
            file.write("\n".join(summary))
        logger.info(f"Raport podsumowujący zapisany: {SUMMARY_REPORT_PATH}")
        print(f"\n ✅ Raport podsumowujący zapisany:\n 📂 {SUMMARY_REPORT_PATH}")
        time.sleep(2.5)
    except IOError as e:
        logger.error(f"Błąd zapisywania raportu podsumowującego: {e}\n")
        print(f" ❌ Błąd zapisywania raportu: {e}\n")


if __name__ == "__main__":
    generate_summary()
