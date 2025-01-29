#!/usr/bin/env python3
# ai_assistant/scripts/generate_user_report.py
# ==================================================
# Script for generating a report on WireGuard users and configuration.
# Version: 1.4
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

USER_REPORT_FILE = BASE_DIR / "ai_assistant/outputs/user_report.txt"
SERVER_CONFIG_FILE = Path("/etc/wireguard/wg0.conf")
PARAMS_FILE = Path("/etc/wireguard/params")

def parse_wg_config(config_path):
    """Reads WireGuard configuration and extracts client information."""
    clients = []
    current_client = None

    try:
        with open(config_path, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith("### Client"):
                    if current_client:
                        clients.append(current_client)
                    current_client = {"login": line.split("### Client")[-1].strip(), "peer": {}}
                elif line.startswith("[Peer]"):
                    continue
                elif "=" in line and current_client:
                    key, value = map(str.strip, line.split("=", 1))
                    current_client["peer"][key] = value
            if current_client:
                clients.append(current_client)
    except FileNotFoundError:
        print(f"Configuration file {config_path} not found.")
        sys.exit(1)

    return clients

def get_wg_status():
    """Gets WireGuard status using the `wg show` command."""
    try:
        output = subprocess.check_output(["wg", "show"], text=True).splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error executing wg show command: {e}")
        sys.exit(1)

    peers = {}
    current_peer = None

    for line in output:
        if line.startswith("peer:"):
            if current_peer:
                peers[current_peer["PublicKey"]] = current_peer
            current_peer = {"PublicKey": line.split("peer:")[1].strip(), "Transfer": {}}
        elif "latest handshake:" in line and current_peer:
            current_peer["LatestHandshake"] = line.split("latest handshake:")[1].strip()
        elif "transfer:" in line and current_peer:
            transfer_data = line.split("transfer:")[1].strip().split(",")
            current_peer["Transfer"] = {
                "Received": transfer_data[0].strip(),
                "Sent": transfer_data[1].strip()
            }

    if current_peer:
        peers[current_peer["PublicKey"]] = current_peer

    return peers

def read_params_file(filepath):
    """Reads the WireGuard parameters file."""
    try:
        with open(filepath, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"File {filepath} not found.")
        return ""

def generate_user_report(clients, wg_status, params_data):
    """Generates a text report on WireGuard users."""
    active_users = []
    inactive_users = []
    all_logins = []

    for client in clients:
        login = client.get("login", "Unknown")
        peer = client.get("peer", {})
        public_key = peer.get("PublicKey", "Unknown")
        allowed_ip = peer.get("AllowedIPs", "Unknown")

        wg_peer_status = wg_status.get(public_key, {})
        transfer = wg_peer_status.get("Transfer", {"Received": "0 MiB", "Sent": "0 MiB"})

        if any(float(value.split()[0]) > 0 for value in transfer.values()):
            active_users.append(f"- {allowed_ip} - {login}: Incoming: {transfer['Received']}, Outgoing: {transfer['Sent']}")
        else:
            inactive_users.append(f"- {allowed_ip} - {login}")

        all_logins.append(login)

    report = [
        "=== Summary ===",
        f"- Total Users: {len(all_logins)}",
        f"- User Logins: {', '.join(all_logins)}",
        "\nActive Users:",
    ]

    if active_users:
        report.extend(active_users)
    else:
        report.append("- No active users.")

    report.append("\nInactive Users:")
    if inactive_users:
        report.extend(inactive_users)
    else:
        report.append("- No inactive users.")

    report.append("\n=== WireGuard Parameters ===")
    report.append(params_data if params_data else "- No parameters found.")

    report.append("")
    return "\n".join(report)

def main():
    clients = parse_wg_config(SERVER_CONFIG_FILE)
    wg_status = get_wg_status()
    params_data = read_params_file(PARAMS_FILE)
    report = generate_user_report(clients, wg_status, params_data)

    with open(USER_REPORT_FILE, "w") as file:
        file.write(report)

    print(f"User report has been saved to {USER_REPORT_FILE}")

if __name__ == "__main__":
    main()
