#!/usr/bin/env python3
# modules/report_utils.py
# ===========================================
# Moduł do obsługi raportów w projekcie pyWGgen
# ===========================================
# Moduł dostarcza funkcje do generowania i wyświetlania raportów,
# w tym raportów pełnych, krótkich, podsumowań oraz informacji o stanie projektu.
#
# Wersja: 2.1
# Aktualizacja: 2024-12-10

import os
import json
import subprocess
import platform
import psutil
import time
from datetime import datetime
from termcolor import colored
from pathlib import Path
from modules.firewall_utils import get_external_ip
from settings import SUMMARY_REPORT_PATH, TEST_REPORT_PATH
from modules.report_generator import generate_report

# Ścieżka do skryptu tworzącego summary_report
SUMMARY_SCRIPT = Path(__file__).resolve().parent.parent / "modules" / "diagnostics_summary.py"

from datetime import datetime, timedelta

def create_summary_report():
    """Sprawdza czy raport jest aktualny i wywołuje skrypt do utworzenia summary_report.txt jeśli potrzeba."""
    try:
        # Sprawdź czy plik istnieje
        if SUMMARY_REPORT_PATH.exists():
            # Pobierz czas ostatniej modyfikacji pliku
            last_modified = datetime.fromtimestamp(SUMMARY_REPORT_PATH.stat().st_mtime)
            age = datetime.now() - last_modified

            if age < timedelta(minutes=1):
                print(f" ✅ Plik {SUMMARY_REPORT_PATH} jest aktualny. Nie wymaga ponownego utworzenia.")
                return
            else:
                print(f" ⏳ Plik {SUMMARY_REPORT_PATH} jest nieaktualny ({age.seconds // 60} minut). Odświeżanie...")

        else:
            print(f" ⏳ Plik {SUMMARY_REPORT_PATH} nie istnieje. Tworzenie...")

        # Wywołanie przez Python
        subprocess.run(["python3", str(SUMMARY_SCRIPT)], check=True)
        
        print(f" ✅ Plik {SUMMARY_REPORT_PATH} pomyślnie utworzony.")
    except subprocess.CalledProcessError as e:
        print(f" ❌ Błąd uruchamiania skryptu {SUMMARY_SCRIPT}: {e}")
    except Exception as e:
        print(f" ❌ Nieoczekiwany błąd podczas tworzenia pliku {SUMMARY_REPORT_PATH}: {e}")

def get_open_ports():
    """Zwraca listę otwartych portów w firewalld."""
    try:
        output = subprocess.check_output(["sudo", "firewall-cmd", "--list-ports"], text=True)
        return output.strip() if output else colored("Brak otwartych portów ❌", "red")
    except subprocess.CalledProcessError:
        return colored("Błąd pobierania danych ❌", "red")

def get_wireguard_status():
    """Zwraca status WireGuard."""
    try:
        output = subprocess.check_output(["systemctl", "is-active", "wg-quick@wg0"], text=True).strip()
        if output == "active":
            return colored("aktywny ✅", "green")
        return colored("nieaktywny ❌", "red")
    except subprocess.CalledProcessError:
        return colored("nie zainstalowany ❌", "red")

def get_wireguard_peers():
    """Pobiera listę aktywnych peerów WireGuard."""
    try:
        output = subprocess.check_output(["wg", "show"], text=True).splitlines()
        peers = [line.split(":")[1].strip() for line in output if line.startswith("peer:")]
        if peers:
            return f"{len(peers)} aktywnych peerów ✅"
        return colored("Brak aktywnych peerów ❌", "red")
    except FileNotFoundError:
        return colored("Komenda 'wg' nie znaleziona ❌", "red")
    except subprocess.CalledProcessError:
        return colored("Błąd pobierania danych ❌", "red")

def get_users_data():
    """Pobiera informacje o użytkownikach z user_records.json."""
    user_records_path = os.path.join("user", "data", "user_records.json")
    try:
        with open(user_records_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return colored("Plik user_records.json nie istnieje ❌", "red")
    except json.JSONDecodeError:
        return colored("Plik user_records.json jest uszkodzony ❌", "red")

def get_gradio_status(port=7860):
    """Sprawdza status Gradio."""
    try:
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            cmdline = proc.info.get("cmdline", [])
            if cmdline and "gradio" in " ".join(cmdline) and str(port) in " ".join(cmdline):
                return f"działa (PID {proc.info['pid']}) ✅"
        return colored("nie działa ❌", "red")
    except Exception as e:
        return colored(f"Błąd sprawdzania Gradio: {e} ❌", "red")

def get_gradio_port_status(port=7860):
    """Sprawdza czy port Gradio jest otwarty."""
    open_ports = get_open_ports()
    if f"{port}/tcp" in open_ports:
        return colored("otwarty ✅", "green")
    return colored("zamknięty ❌", "red")

def show_project_status():
    """Wyświetla status projektu."""
    print("=== Podsumowanie statusu projektu ===\n")

    # Informacje systemowe
    print(f" 🖥️   System: {platform.system()} {platform.release()}")
    print(f" 🧰  Jądro: {platform.uname().release}")
    print(f" 🌍  Zewnętrzny adres IP: {get_external_ip()}")

    # Status WireGuard
    print(f" 🛡️   Status WireGuard: {get_wireguard_status()}")
    config_path = "/etc/wireguard/wg0.conf"
    print(f" ⚙️   Plik konfiguracyjny: {config_path if os.path.exists(config_path) else colored('brakuje ❌', 'red')}")
    print(f" 🌐  Aktywni peerzy: {get_wireguard_peers()}")

    # Ostatni raport
    report_path = os.path.join("pyWGgen", "test_report.txt")
    if os.path.exists(report_path):
        print(f" 📋  Ostatni raport: {report_path}")
    else:
        print(colored(" 📋  Ostatni raport: brakuje ❌", "red"))

    print("\n===========================================\n")

def generate_project_report():
    """Generuje pełny raport."""
    print("\n  📋  Generowanie pełnego raportu...")
    try:
        generate_report()
    except Exception as e:
        print(f" ❌ Błąd generowania pełnego raportu: {e}")

def display_test_report():
    """Wyświetla zawartość pełnego raportu w konsoli."""
    if TEST_REPORT_PATH.exists():
        with open(TEST_REPORT_PATH, "r", encoding="utf-8") as file:
            print(file.read())
    else:
        print(f"  ❌  Plik pełnego raportu nie znaleziony: {TEST_REPORT_PATH}")

def display_test_summary():
    """Wyświetla krótki raport."""
    if TEST_REPORT_PATH.exists():
        with open(TEST_REPORT_PATH, "r", encoding="utf-8") as file:
            lines = file.readlines()
            summary_keys = [
                "Data i czas",
                "Status WireGuard",
                "Gradio",
                "Otwarte porty",
                "wg0.conf"
            ]
            print("\n=== Krótki raport statusu projektu ===")
            for line in lines:
                if any(key in line for key in summary_keys):
                    print(line.strip())
            print("\n=========================================")
    else:
        print(f"  ❌  Plik raportu statusu projektu nie znaleziony: {TEST_REPORT_PATH}")

def display_summary_report():
    """
    Odczytuje i wyświetla zawartość raportu statusu projektu pyWGgen.
    Używa ścieżki pliku z settings.py.
    Jeśli plik nie istnieje, inicjuje jego utworzenie.
    """
    try:
        if not SUMMARY_REPORT_PATH.exists():
            create_summary_report()

        with open(SUMMARY_REPORT_PATH, "r", encoding="utf-8") as file:
            content = file.read()

        print("\n=== 📋 Raport statusu projektu pyWGgen ===\n")
        print(content)

    except Exception as e:
        print(f" ❌ Błąd odczytu raportu statusu projektu pyWGgen: {e}")

if __name__ == "__main__":
    show_project_status()
    time.sleep(2)
    print("\n=== Wykonywanie operacji raportów ===\n")
    display_summary_report()
