#!/usr/bin/env python3
# ai_assistant/scripts/final_wg_report.py
# ==================================================
# Скрипт для создания структурированного отчета
# на основе данных из wg_raw_data.txt.
# Версия: 1.0 (2024-12-21)
# ==================================================

import re

INPUT_FILE = "wg_raw_data.txt"
OUTPUT_FILE = "wg_final_report.txt"

def parse_wg_raw_data(input_file):
    """Парсит сырые данные из wg_raw_data.txt."""
    server_config = []
    clients = []
    wg_status = []
    parameters = []

    with open(input_file, 'r') as file:
        section = None
        for line in file:
            line = line.strip()

            # Определяем текущую секцию
            if line.startswith("[WireGuard Configuration File]"):
                section = "server_config"
            elif line.startswith("[WireGuard Status (`wg show`)]"):
                section = "wg_status"
            elif line.startswith("[WireGuard Parameters File]"):
                section = "parameters"
            elif line.startswith("### Client"):
                section = "clients"

            # Заполняем данные
            if section == "server_config" and not line.startswith("["):
                server_config.append(line)
            elif section == "clients" and not line.startswith("["):
                clients.append(line)
            elif section == "wg_status" and not line.startswith("["):
                wg_status.append(line)
            elif section == "parameters" and not line.startswith("["):
                parameters.append(line)

    return {
        "server_config": server_config,
        "clients": clients,
        "wg_status": wg_status,
        "parameters": parameters,
    }

def analyze_clients(clients, wg_status):
    """Анализирует список клиентов и их активность."""
    logins = []
    active_clients = []
    inactive_clients = []

    # Сопоставление ключей пользователей с их логинами
    peer_to_login = {}
    for client in clients:
        if client.startswith("### Client"):
            current_login = client.split("### Client")[1].strip()
        elif "PublicKey =" in client:
            public_key = client.split("PublicKey =")[1].strip()
            peer_to_login[public_key] = current_login

    # Анализ активности пиров
    current_peer = None
    for line in wg_status:
        line = line.strip()
        if line.startswith("peer:"):
            if current_peer:
                # Проверяем активность предыдущего пира
                traffic = current_peer.get("traffic")
                if traffic and any(float(t.split()[0]) > 0 for t in traffic.values()):
                    active_clients.append(current_peer)
                else:
                    inactive_clients.append(current_peer)

            # Начинаем обработку нового пира
            peer_key = line.split("peer:")[1].strip()
            current_peer = {
                "public_key": peer_key,
                "login": peer_to_login.get(peer_key, "Unknown"),
                "traffic": {"received": "0 MiB", "sent": "0 MiB"}
            }

        elif "transfer:" in line and current_peer:
            transfer_data = line.split("transfer:")[1].strip().split(",")
            current_peer["traffic"] = {
                "received": transfer_data[0].strip(),
                "sent": transfer_data[1].strip()
            }

    # Проверяем последний обработанный пир
    if current_peer:
        traffic = current_peer.get("traffic")
        if traffic and any(float(t.split()[0]) > 0 for t in traffic.values()):
            active_clients.append(current_peer)
        else:
            inactive_clients.append(current_peer)

    return logins, active_clients, inactive_clients

def generate_report(parsed_data):
    """Генерирует финальный отчет."""
    logins, active_clients, inactive_clients = analyze_clients(parsed_data["clients"], parsed_data["wg_status"])

    with open(OUTPUT_FILE, 'w') as file:
        # Summary
        file.write("=== Summary ===\n")
        file.write(f"- Total Users: {len(logins)}\n")
        file.write(f"- User Logins: {', '.join(logins)}\n\n")

        file.write("Active Users:\n")
        if active_clients:
            for client in active_clients:
                file.write(f"- {client}\n")
        else:
            file.write("- No active users.\n")

        file.write("\nInactive Users:\n")
        if inactive_clients:
            for client in inactive_clients:
                file.write(f"- {client}\n")
        else:
            file.write("- All users are active.\n")

        # Server Configuration
        file.write("\n=== Server Configuration ===\n")
        for line in parsed_data["server_config"]:
            file.write(f"{line}\n")

        # WireGuard Status
        file.write("\n=== WireGuard Status ===\n")
        for line in parsed_data["wg_status"]:
            file.write(f"{line}\n")

        # WireGuard Parameters
        file.write("\n=== WireGuard Parameters ===\n")
        for line in parsed_data["parameters"]:
            file.write(f"{line}\n")

    print(f"Final report has been saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    # Parse the raw data
    parsed_data = parse_wg_raw_data(INPUT_FILE)

    # Generate the final report
    generate_report(parsed_data)
