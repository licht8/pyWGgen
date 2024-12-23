#!/usr/bin/env python3
# ai_assistant/scripts/final_wg_report.py
# ==================================================
# Скрипт для создания двух файлов отчетов из wg_raw_data.txt:
# - wg_final_report_part1.txt (данные пользователей и сервера)
# - wg_final_report_part2.txt (системная информация и прочее)
# Версия: 2.0 (2024-12-23)
# ==================================================

import re
import subprocess

RAW_DATA_FILE = "wg_raw_data.txt"
PART1_REPORT_FILE = "wg_final_report_part1.txt"
PART2_REPORT_FILE = "wg_final_report_part2.txt"

def load_raw_data(filepath):
    """Загружает данные из файла wg_raw_data.txt."""
    with open(filepath, "r") as file:
        return file.readlines()

def parse_server_and_users(raw_data):
    """Извлекает информацию о пользователях и сервере для первой части отчета."""
    part1_data = []
    capture = True

    for line in raw_data:
        if line.strip() == "=== System Information ===":
            capture = False  # Завершаем сбор данных для первой части
        if capture:
            part1_data.append(line.strip())

    return part1_data

def parse_system_info(raw_data):
    """Извлекает системную информацию для второй части отчета."""
    part2_data = []
    capture = False

    for line in raw_data:
        if line.strip() == "=== System Information ===":
            capture = True
        if capture:
            part2_data.append(line.strip())

    return part2_data

def collect_additional_info():
    """Собирает дополнительную системную информацию и возвращает ее в формате текста."""
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
    info = []
    for title, command in commands.items():
        try:
            output = subprocess.check_output(command, shell=True, text=True)
            info.append(f"=== {title} ===\n{output.strip()}")
        except subprocess.CalledProcessError as e:
            info.append(f"=== {title} ===\nError: {e}")
    return "\n\n".join(info)

def save_report(filepath, data):
    """Сохраняет данные в указанный файл."""
    with open(filepath, "w") as file:
        file.write("\n".join(data) + "\n")
    print(f"Report saved to {filepath}")

def main():
    raw_data = load_raw_data(RAW_DATA_FILE)

    # Генерация первой части отчета
    part1_data = parse_server_and_users(raw_data)
    save_report(PART1_REPORT_FILE, part1_data)

    # Генерация второй части отчета
    part2_data = parse_system_info(raw_data)

    # Добавление дополнительной информации
    additional_info = collect_additional_info()
    part2_data.append("\n=== Additional System Information ===")
    part2_data.append(additional_info)
    
    save_report(PART2_REPORT_FILE, part2_data)

if __name__ == "__main__":
    main()
