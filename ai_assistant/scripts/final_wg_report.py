#!/usr/bin/env python3
# ai_assistant/scripts/final_wg_report.py
# ==================================================
# Скрипт для создания структурированного отчета
# на основе данных из wg_raw_data.txt.
# Версия: 1.3 (2024-12-23)
# ==================================================

import re
import subprocess
import os
from datetime import datetime

RAW_DATA_FILE = "wg_raw_data.txt"
FINAL_REPORT_FILE = "wg_final_report.txt"

def load_raw_data(filepath):
    """Загружает данные из файла wg_raw_data.txt."""
    with open(filepath, "r") as file:
        return file.readlines()

def parse_server_config(raw_data):
    """Извлекает конфигурацию сервера, исключая приватные ключи."""
    server_config = []
    capture = False
    for line in raw_data:
        if "[WireGuard Configuration File]" in line:
            capture = True
        elif "### Client" in line:
            capture = False
        if capture and line.strip() and "PrivateKey" not in line:
            server_config.append(line.strip())
    return server_config

def parse_wireguard_params(raw_data):
    """Извлекает параметры WireGuard, исключая приватные ключи."""
    params = []
    capture = False
    for line in raw_data:
        if "[WireGuard Parameters File]" in line:
            capture = True
        elif capture and line.strip() and "SERVER_PRIV_KEY" not in line:
            params.append(line.strip())
    return params

def analyze_clients(raw_data):
    """Анализирует клиентов и их активность."""
    logins = []
    active_clients = []
    inactive_clients = []

    peer_to_login = {}
    peer_to_ip = {}
    capture_clients = False
    current_peer = None

    for line in raw_data:
        line = line.strip()

        if line.startswith("### Client"):
            capture_clients = True
            current_login = line.split("### Client")[1].strip()

        elif line.startswith("[Peer]"):
            capture_clients = True
            continue

        elif capture_clients and "=" in line:
            key, value = map(str.strip, line.split("=", 1))
            if key == "PublicKey":
                peer_to_login[value] = current_login
                logins.append(current_login)
            elif key == "AllowedIPs":
                peer_to_ip[current_login] = value

        if "peer:" in line:
            if current_peer:
                traffic = current_peer.get("traffic")
                if traffic and any(float(t.split()[0]) > 0 for t in traffic.values()):
                    active_clients.append(current_peer)
                else:
                    inactive_clients.append(current_peer)

            peer_key = line.split("peer:")[1].strip()
            current_peer = {
                "public_key": peer_key,
                "login": peer_to_login.get(peer_key, "Unknown"),
                "ip_address": peer_to_ip.get(peer_to_login.get(peer_key, ""), "Unknown"),
                "traffic": {"received": "0 MiB", "sent": "0 MiB"}
            }

        elif "transfer:" in line and current_peer:
            transfer_data = line.split("transfer:")[1].strip().split(",")
            current_peer["traffic"] = {
                "received": transfer_data[0].strip(),
                "sent": transfer_data[1].strip()
            }

    if current_peer:
        traffic = current_peer.get("traffic")
        if traffic and any(float(t.split()[0]) > 0 for t in traffic.values()):
            active_clients.append(current_peer)
        else:
            inactive_clients.append(current_peer)

    return logins, active_clients, inactive_clients

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
        "VPN Logs (Last 10 Lines)": "sudo journalctl -u wg-quick@wg0 -n 10",
        "System Logs (Last 10 VPN Errors)": "sudo journalctl | grep -i wireguard | tail -n 10"
    }
    system_info = {}
    for section, command in commands.items():
        try:
            result = subprocess.check_output(command, shell=True, text=True)
            system_info[section] = result.strip()
        except subprocess.CalledProcessError:
            system_info[section] = "-- Command failed or no data available --"
    return system_info

def generate_final_report(server_config, wg_params, logins, active_clients, inactive_clients, additional_info):
    """Генерирует финальный отчет."""
    report = []

    # Summary
    report.append("=== Summary ===")
    report.append(f"- Total Users: {len(logins)}")
    report.append(f"- User Logins: {', '.join(logins)}")
    report.append("\nActive Users:")
    if active_clients:
        for client in active_clients:
            report.append(
                f"- {client['ip_address']} - {client['login']}: Incoming: {client['traffic']['received']}, Outgoing: {client['traffic']['sent']}"
            )
    else:
        report.append("- No active users.")

    report.append("\nInactive Users:")
    if inactive_clients:
        for client in inactive_clients:
            report.append(
                f"- {client['ip_address']} - {client['login']}"
            )
    else:
        report.append("- No inactive users.")

    # Server Configuration
    report.append("\n=== Server Configuration ===")
    report.extend(server_config)

    # WireGuard Parameters
    report.append("\n=== WireGuard Parameters ===")
    report.extend(wg_params)

    # Additional System Info
    report.append("\n=== System Information ===")
    for section, content in additional_info.items():
        report.append(f"=== {section} ===")
        if content:
            report.extend(content.splitlines())
        else:
            report.append("-- No entries --")

    # Добавляем пустую строку в конец отчета
    report.append("")  # Пустая строка

    return "\n".join(report)

def main():
    raw_data = load_raw_data(RAW_DATA_FILE)
    server_config = parse_server_config(raw_data)
    wg_params = parse_wireguard_params(raw_data)
    logins, active_clients, inactive_clients = analyze_clients(raw_data)
    additional_info = collect_system_info()
    final_report = generate_final_report(server_config, wg_params, logins, active_clients, inactive_clients, additional_info)

    with open(FINAL_REPORT_FILE, "w") as file:
        file.write(final_report)
        file.write("\n")  # Пустая строка в конце файла

    print(f"Final report has been saved to {FINAL_REPORT_FILE}")

if __name__ == "__main__":
    main()
