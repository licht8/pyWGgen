#!/usr/bin/env python3
# ai_assistant/scripts/generate_system_report.py
# ==================================================
# Скрипт для создания системного отчета WireGuard.
# Версия: 1.3
# ==================================================

import subprocess
import os
import sys
from pathlib import Path

# Добавление корневого пути проекта для импорта settings
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = SCRIPT_DIR.parent.parent
    sys.path.append(str(PROJECT_ROOT))
    from settings import BASE_DIR
except ImportError as e:
    print(f"Ошибка импорта settings: {e}")
    sys.exit(1)

SYSTEM_REPORT_FILE = BASE_DIR / "ai_assistant/outputs/system_report.txt"


def run_command(command):
    """Выполняет команду и возвращает ее вывод."""
    try:
        return subprocess.check_output(command, shell=True, text=True).strip()
    except subprocess.CalledProcessError as e:
        return f"Ошибка выполнения команды {command}: {e}"


def generate_system_report():
    """Создает системный отчет."""
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
