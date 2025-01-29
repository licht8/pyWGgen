#!/usr/bin/env python3
# ai_assistant/scripts/generate_system_report.py
# ==================================================
# Script for generating a WireGuard system report.
# Version: 1.3
# ==================================================

import subprocess
import os
import sys
from pathlib import Path

# Adding the project root path for importing settings
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = SCRIPT_DIR.parent.parent
    sys.path.append(str(PROJECT_ROOT))
    from settings import BASE_DIR
except ImportError as e:
    print(f"Error importing settings: {e}")
    sys.exit(1)

SYSTEM_REPORT_FILE = BASE_DIR / "ai_assistant/outputs/system_report.txt"


def run_command(command):
    """Executes a command and returns its output."""
    try:
        return subprocess.check_output(command, shell=True, text=True).strip()
    except subprocess.CalledProcessError as e:
        return f"Error executing command {command}: {e}"


def generate_system_report():
    """Generates a system report."""
    report = [
        "=== System Information ===",
        run_command("uname -a"),
        "\n=== Firewall Configuration ===",
        run_command("sudo firewall-cmd --list-all"),
        "\n=== IP Routes ===",
        run_command("ip route"),
        "\n=== Disk Usage ===",
        run_command("df -h"),
        "\n=== Memory Usage ===",
        run_command("free -h"),
        "\n=== CPU Information ===",
        run_command("lscpu"),
        "\n=== VPN Logs (Last 10 Lines) ===",
        run_command("sudo journalctl -u wg-quick@wg0 | tail -n 10"),
        "\n=== System Logs (Last 10 VPN Errors) ===",
        run_command("sudo journalctl | grep -i wireguard | tail -n 10"),
        ""
    ]
    return "\n".join(report)


def main():
    report = generate_system_report()

    with open(SYSTEM_REPORT_FILE, "w") as file:
        file.write(report)

    print(f"System report has been saved to {SYSTEM_REPORT_FILE}")


if __name__ == "__main__":
    main()
