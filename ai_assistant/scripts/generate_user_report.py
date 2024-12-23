#!/usr/bin/env python3
# ai_assistant/scripts/generate_user_report.py
# ==================================================
# Скрипт для создания отчета о пользователях и конфигурации WireGuard.
# Версия: 1.1
# ==================================================

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
    """Анализирует клиентов и их активность."""
    logins, active_clients, inactive_clients = [], [], []
    peer_to_login, peer_to_ip = {}, {}
    current_peer = None

    for line in raw_data:
        line = line.strip()
        if line.startswith("### Client"):
            current_login = line.split("### Client")[1].strip()
        elif line.startswith("[Peer]"):
            current_peer = {"login": current_login, "ip": None, "traffic": {"received": "0 MiB", "sent": "0 MiB"}}
        elif "=" in line:
            key, value = map(str.strip, line.split("=", 1))
            if key == "AllowedIPs":
                current_peer["ip"] = value
            elif key == "PublicKey":
                peer_to_login[value] = current_login
        elif "transfer:" in line and current_peer:
            received, sent = line.split("transfer:")[1].split(",")
            current_peer["traffic"] = {"received": received.strip(), "sent": sent.strip()}
            if float(received.split()[0]) > 0 or float(sent.split()[0]) > 0:
                active_clients.append(current_peer)
            else:
                inactive_clients.append(current_peer)

    # Ensure all clients are accounted for
    for login in peer_to_login.values():
        if login not in [client["login"] for client in active_clients + inactive_clients]:
            inactive_clients.append({"login": login, "ip": peer_to_ip.get(login, "Unknown"), "traffic": {"received": "0 MiB", "sent": "0 MiB"}})

    logins = list(peer_to_login.values())
    return logins, active_clients, inactive_clients

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
