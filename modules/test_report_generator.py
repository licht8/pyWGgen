#!/usr/bin/env python3
# modules/test_report_generator.py
# Script for generating a complete report on the state of the wg_qr_generator project
# Version: 2.1
# Updated: 2024-12-10
# Purpose: Generate a detailed report for diagnosing the project's state.

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from prettytable import PrettyTable

# Add the project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import settings
from settings import TEST_REPORT_PATH, USER_DB_PATH, WG_CONFIG_DIR, GRADIO_PORT

def load_json(filepath):
    """Loads data from a JSON file."""
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return f" ❌  File {filepath} is missing."
    except json.JSONDecodeError:
        return f" ❌  File {filepath} is corrupted."

def run_command(command):
    """Executes a command and returns the output."""
    try:
        return subprocess.check_output(command, text=True).strip()
    except FileNotFoundError:
        return f" ❌  Command '{command[0]}' not found."
    except subprocess.CalledProcessError as e:
        return f" ❌  Error executing command {' '.join(command)}: {e}"

def get_gradio_status():
    """Checks the status of Gradio."""
    try:
        output = subprocess.check_output(["ps", "-eo", "pid,cmd"], text=True)
        for line in output.splitlines():
            if "gradio" in line and str(GRADIO_PORT) in line:
                return f" 🟢  Gradio is running (line: {line})"
        return " ❌  Gradio is not running"
    except Exception as e:
        return f" ❌  Error checking Gradio: {e}"

def generate_report():
    """Generates a complete report on the project's state."""
    timestamp = datetime.utcnow().isoformat()
    user_records = load_json(USER_DB_PATH)

    report_lines = [
        f"\n === 📝  Project wg_qr_generator Status Report  ===",
        f" 📅  Date and Time: {timestamp}\n"
    ]

    # Project structure check
    report_lines.append(" === 📂  Project Structure Check  ===")
    required_files = {
        "user_records.json": USER_DB_PATH,
        "wg_configs": WG_CONFIG_DIR,
    }
    for name, path in required_files.items():
        report_lines.append(f"- {name}: {' 🟢  Present' if Path(path).exists() else ' ❌  Missing'}")

    required_dirs = ["logs", "user/data", "user/data/qrcodes", "user/data/wg_configs"]
    for folder in required_dirs:
        report_lines.append(f"- {folder}: {' 🟢  Exists' if os.path.exists(folder) else ' ❌  Missing'}")

    # Data from JSON
    report_lines.append("\n === 📄  Data from user_records.json  ===")
    if isinstance(user_records, dict):
        table = PrettyTable(["User", "peer", "telegram_id"])
        for username, data in user_records.items():
            table.add_row([username, data.get('peer', 'N/A'), data.get('telegram_id', 'N/A')])
        report_lines.append(str(table))
    else:
        report_lines.append(f"{user_records}\n")

    # WireGuard check
    report_lines.append("\n === 🔒  WireGuard Results (wg show)  ===")
    wg_show_output = run_command(["wg", "show"])
    report_lines.append(wg_show_output if wg_show_output else " ❌  WireGuard is not running or encountered an error.\n")

    # WireGuard status
    report_lines.append("\n === 🔧  WireGuard Status  ===")
    wg_status_output = run_command(["systemctl", "status", "wg-quick@wg0"])
    report_lines.append(wg_status_output)

    # Open ports check
    report_lines.append("\n === 🔍  Open Ports Check  ===")
    firewall_ports = run_command(["sudo", "firewall-cmd", "--list-ports"])
    report_lines.append(f"Open Ports: {firewall_ports}")

    # Gradio status
    report_lines.append("\n === 🌐  Gradio Status  ===")
    gradio_status = get_gradio_status()
    report_lines.append(f"Gradio: {gradio_status}")

    # Active processes
    report_lines.append("\n === 🖥️  Active Processes  ===")
    try:
        ps_output = subprocess.check_output(["ps", "-eo", "pid,cmd"], text=True)
        report_lines.append(ps_output)
    except subprocess.CalledProcessError:
        report_lines.append(" ❌  Error fetching process list.")

    # Save the report
    with open(TEST_REPORT_PATH, "w", encoding="utf-8") as report_file:
        report_file.write("\n".join(report_lines))

    print(f"  ✅  Report saved at:\n  📂 {TEST_REPORT_PATH}")

if __name__ == "__main__":
    generate_report()
