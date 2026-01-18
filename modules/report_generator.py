#!/usr/bin/env python3
# modules/report_generator.py
# Skrypt do generowania kompletnego raportu o stanie projektu pyWGgen
# Wersja: 2.1
# Aktualizacja: 2024-12-10
# Cel: Generowanie szczegółowego raportu diagnostycznego stanu projektu.

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from prettytable import PrettyTable

# Dodaj katalog główny projektu do sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import ustawień
from settings import TEST_REPORT_PATH, USER_DB_PATH, WG_CONFIG_DIR, GRADIO_PORT

def load_json(filepath):
    """Wczytuje dane z pliku JSON."""
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return f" ❌  Plik {filepath} nie istnieje."
    except json.JSONDecodeError:
        return f" ❌  Plik {filepath} jest uszkodzony."

def run_command(command):
    """Wykonuje polecenie i zwraca wynik."""
    try:
        return subprocess.check_output(command, text=True).strip()
    except FileNotFoundError:
        return f" ❌  Polecenie '{command[0]}' nie znalezione."
    except subprocess.CalledProcessError as e:
        return f" ❌  Błąd wykonywania polecenia {' '.join(command)}: {e}"

def get_gradio_status():
    """Sprawdza status Gradio."""
    try:
        output = subprocess.check_output(["ps", "-eo", "pid,cmd"], text=True)
        for line in output.splitlines():
            if "gradio" in line and str(GRADIO_PORT) in line:
                return f" 🟢  Gradio działa (linia: {line})"
        return " ❌  Gradio nie działa"
    except Exception as e:
        return f" ❌  Błąd sprawdzania Gradio: {e}"

def generate_report():
    """Generuje kompletny raport o stanie projektu."""
    timestamp = datetime.utcnow().isoformat()
    user_records = load_json(USER_DB_PATH)

    report_lines = [
        f"\n === 📝  Raport statusu generatora projektu  ===",
        f" 📅  Data i czas: {timestamp}\n"
    ]

    # Sprawdzenie struktury projektu
    report_lines.append(" === 📂  Sprawdzenie struktury projektu  ===")
    required_files = {
        "user_records.json": USER_DB_PATH,
        "wg_configs": WG_CONFIG_DIR,
    }
    for name, path in required_files.items():
        report_lines.append(f"- {name}: {' 🟢  Istnieje' if Path(path).exists() else ' ❌  Brakuje'}")

    required_dirs = ["logs", "user/data", "user/data/qrcodes", "user/data/wg_configs"]
    for folder in required_dirs:
        report_lines.append(f"- {folder}: {' 🟢  Istnieje' if os.path.exists(folder) else ' ❌  Brakuje'}")

    # Dane z JSON
    report_lines.append("\n === 📄  Dane z user_records.json  ===")
    if isinstance(user_records, dict):
        table = PrettyTable(["Użytkownik", "peer", "telegram_id"])
        for username, data in user_records.items():
            table.add_row([username, data.get('peer', 'N/A'), data.get('telegram_id', 'N/A')])
        report_lines.append(str(table))
    else:
        report_lines.append(f"{user_records}\n")

    # Sprawdzenie WireGuard
    report_lines.append("\n === 🔒  Wyniki WireGuard (wg show)  ===")
    wg_show_output = run_command(["wg", "show"])
    report_lines.append(wg_show_output if wg_show_output else " ❌  WireGuard nie działa lub wystąpił błąd.\n")

    # Status WireGuard
    report_lines.append("\n === 🔧  Status WireGuard  ===")
    wg_status_output = run_command(["systemctl", "status", "wg-quick@wg0"])
    report_lines.append(wg_status_output)

    # Sprawdzenie otwartych portów
    report_lines.append("\n === 🔍  Sprawdzenie otwartych portów  ===")
    firewall_ports = run_command(["sudo", "firewall-cmd", "--list-ports"])
    report_lines.append(f"Otwarte porty: {firewall_ports}")

    # Status Gradio
    report_lines.append("\n === 🌐  Status Gradio  ===")
    gradio_status = get_gradio_status()
    report_lines.append(f"Gradio: {gradio_status}")

    # Aktywne procesy
    report_lines.append("\n === 🖥️  Aktywne procesy  ===")
    try:
        ps_output = subprocess.check_output(["ps", "-eo", "pid,cmd"], text=True)
        report_lines.append(ps_output)
    except subprocess.CalledProcessError:
        report_lines.append(" ❌  Błąd pobierania listy procesów.")

    # Zapisz raport
    with open(TEST_REPORT_PATH, "w", encoding="utf-8") as report_file:
        report_file.write("\n".join(report_lines))

    print(f"  ✅  Raport zapisany w:\n  📂 {TEST_REPORT_PATH}")

if __name__ == "__main__":
    generate_report()
