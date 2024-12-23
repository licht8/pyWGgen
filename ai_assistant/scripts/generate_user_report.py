#!/usr/bin/env python3
# ai_assistant/scripts/generate_user_report.py
# ==================================================
# Скрипт для создания отчета о пользователях и конфигурации WireGuard.
# Версия: 1.3
# ==================================================

import subprocess

RAW_DATA_FILE = "wg_raw_data.txt"
USER_REPORT_FILE = "user_report.txt"

def load_raw_data(filepath):
    """Загружает данные из файла wg_raw_data.txt."""
    with open(filepath, "r") as file:
        return file.readlines()

def parse_server_config(raw_data):
    """Извлекает конфигурацию сервера."""
    config = []
    capture = False
    for line in raw_data:
        if "[WireGuard Configuration File]" in line:
            capture = True
        elif "### Client" in line:
            capture = False
        if capture and line.strip() and "PrivateKey" not in line:
            config.append(line.strip())
    return config

def parse_wireguard_params(raw_data):
    """Извлекает параметры WireGuard."""
    params = []
    capture = False
    for line in raw_data:
        if "[WireGuard Parameters File]" in line:
            capture = True
        elif capture and line.strip() and "SERVER_PRIV_KEY" not in line:
            params.append(line.strip())
    return params

def analyze_clients(raw_data):
    """Анализирует клиентов и их активность на основе данных WireGuard."""
    logins, active_clients, inactive_clients = [], [], []
    peer_to_login, peer_to_ip = {}, {}

    # Извлечение логинов, публичных ключей и IP из конфигурации
    current_login = None
    for line in raw_data:
        line = line.strip()
        if line.startswith("### Client"):
            current_login = line.split("### Client")[1].strip()
        elif line.startswith("[Peer]"):
            continue
        elif "=" in line:
            key, value = map(str.strip, line.split("=", 1))
            if key == "PublicKey":
                peer_to_login[value] = current_login
            elif key == "AllowedIPs":
                peer_to_ip[current_login] = value

    # Сопоставление данных с выводом команды `wg`
    wg_output = subprocess.check_output(["wg"], text=True).splitlines()
    current_peer = None
    for line in wg_output:
        if line.startswith("peer:"):
            if current_peer:
                # Завершить текущего клиента
                process_client(current_peer, peer_to_login, peer_to_ip, active_clients, inactive_clients)
            current_peer = {"public_key": line.split("peer:")[1].strip(), "traffic": {"received": "0 MiB", "sent": "0 MiB"}}
        elif "transfer:" in line and current_peer:
            transfer_data = line.split("transfer:")[1].strip().split(",")
            current_peer["traffic"] = {
                "received": transfer_data[0].strip(),
                "sent": transfer_data[1].strip()
            }
        elif "allowed ips:" in line and current_peer:
            current_peer["ip"] = line.split("allowed ips:")[1].strip()

    if current_peer:
        process_client(current_peer, peer_to_login, peer_to_ip, active_clients, inactive_clients)

    logins = list(peer_to_login.values())
    return logins, active_clients, inactive_clients

def process_client(peer, peer_to_login, peer_to_ip, active_clients, inactive_clients):
    """Обрабатывает одного клиента."""
    login = peer_to_login.get(peer["public_key"], "Unknown")
    ip = peer.get("ip", peer_to_ip.get(login, "Unknown"))
    traffic = peer["traffic"]
    if any(float(value.split()[0]) > 0 for value in traffic.values()):
        active_clients.append({"login": login, "ip": ip, "traffic": traffic})
    else:
        inactive_clients.append({"login": login, "ip": ip, "traffic": traffic})

def generate_user_report(config, params, logins, active, inactive):
    """Создает текстовый отчет."""
    report = [
        "=== Summary ===",
        f"- Total Users: {len(logins)}",
        f"- User Logins: {', '.join(logins)}",
        "\nActive Users:",
        *[f"- {client['ip']} - {client['login']}: Incoming: {client['traffic']['received']}, Outgoing: {client['traffic']['sent']}" for client in active],
        "\nInactive Users:",
        *[f"- {client['ip']} - {client['login']}" for client in inactive],
        "\n=== Server Configuration ===",
        *config,
        "\n=== WireGuard Parameters ===",
        *params,
        ""
    ]
    return "\n".join(report)

def main():
    raw_data = load_raw_data(RAW_DATA_FILE)
    server_config = parse_server_config(raw_data)
    wg_params = parse_wireguard_params(raw_data)
    logins, active_clients, inactive_clients = analyze_clients(raw_data)
    report = generate_user_report(server_config, wg_params, logins, active_clients, inactive_clients)

    with open(USER_REPORT_FILE, "w") as file:
        file.write(report)
    print(f"User report has been saved to {USER_REPORT_FILE}")

if __name__ == "__main__":
    main()
