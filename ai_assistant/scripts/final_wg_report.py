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

    for client in clients:
        if client.startswith("### Client"):
            login = client.split("### Client")[1].strip()
            logins.append(login)
            continue

        if "peer:" in client:
            match = re.search(r"peer:\s*(\S+)", client)
            if match:
                public_key = match.group(1)
                traffic_match = re.search(r"transfer:\s*(\S+\s\S+),\s*(\S+\s\S+)", client)
                if traffic_match:
                    incoming, outgoing = traffic_match.groups()
                    active_clients.append(f"{login}: Incoming: {incoming}, Outgoing: {outgoing}")
                else:
                    inactive_clients.append(login)

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
