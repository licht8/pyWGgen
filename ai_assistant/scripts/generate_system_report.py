#!/usr/bin/env python3
# ai_assistant/scripts/generate_system_report.py
# ==================================================
# Скрипт для создания отчета о системной информации.
# Версия: 1.0
# ==================================================

import subprocess

SYSTEM_REPORT_FILE = "system_report.txt"

def collect_system_info():
    """Собирает системную информацию."""
    commands = {
        "Firewall Configuration": "sudo firewall-cmd --list-all",
        "IP Routes": "ip route",
        "Kernel and System Info": "uname -a",
        "Hostname Information": "hostnamectl",
        "OS Release": "cat /etc/os-release",
        "CPU Information": "lscpu",
        "Memory Usage": "free -h",
        "Disk Usage": "df -h",
        "Block Devices": "lsblk",
        "VPN Logs (Last 10 Lines)": "sudo journalctl -u wg-quick@wg0 | tail -n 10",
        "System Logs (Last 10 VPN Errors)": "sudo journalctl | grep -i wireguard | tail -n 10"
    }
    report = []
    for title, cmd in commands.items():
        try:
            output = subprocess.check_output(cmd, shell=True, text=True)
            report.append(f"=== {title} ===\n{output.strip()}")
        except subprocess.CalledProcessError:
            report.append(f"=== {title} ===\nError executing command")
    report.append("")
    return "\n".join(report)

def main():
    system_info = collect_system_info()
    with open(SYSTEM_REPORT_FILE, "w") as file:
        file.write(system_info)
    print(f"System report has been saved to {SYSTEM_REPORT_FILE}")

if __name__ == "__main__":
    main()
