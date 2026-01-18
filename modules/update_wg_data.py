#!/usr/bin/env python3
"""
modules/update_wg_data.py

Aktualizuje dane WireGuard:
- Usuwa duplikaty.
- Czyści nazwy użytkowników.
"""

import os
import subprocess
import json
from datetime import datetime

# Ścieżki do plików
WG_CONFIG_PATH = "/etc/wireguard/wg0.conf"
JSON_LOG_PATH = "/root/pyWGgenerator/pyWGgen/logs/wg_users.json"
TEXT_LOG_PATH = "/root/pyWGgenerator/pyWGgen/logs/wg_activity.log"

def parse_wg_show():
    """Odczytuje i parsuje wynik polecenia `wg show`."""
    try:
        output = subprocess.check_output(["wg"], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Błąd uruchamiania `wg`: {e}")
        return None

    peers = {}
    current_peer = None

    for line in output.splitlines():
        if line.startswith("peer:"):
            current_peer = line.split(":")[1].strip()
            peers[current_peer] = {"transfer": {"received": 0, "sent": 0}, "latest_handshake": None}
        elif line.strip().startswith("transfer:"):
            parts = line.strip().split(",")
            received = parts[0].split()[1]
            sent = parts[1].split()[1]
            peers[current_peer]["transfer"] = {"received": received, "sent": sent}
        elif line.strip().startswith("latest handshake:"):
            handshake = line.split(":")[1].strip()
            peers[current_peer]["latest_handshake"] = handshake

    return peers

def parse_wg_conf():
    """Odczytuje konfigurację WireGuard do mapowania użytkowników."""
    try:
        with open(WG_CONFIG_PATH, "r") as f:
            config = f.read()
    except FileNotFoundError:
        print(f"Plik {WG_CONFIG_PATH} nie znaleziony.")
        return None

    users = {}
    current_peer = None

    for line in config.splitlines():
        if line.strip().startswith("[Peer]"):
            current_peer = None
        elif line.strip().startswith("PublicKey ="):
            current_peer = line.split("=")[1].strip()
            users[current_peer] = {"username": None, "allowed_ips": None}
        elif line.strip().startswith("#"):
            if current_peer:
                username = line.strip("#").strip()
                if username.startswith("Client "):
                    username = username.replace("Client ", "", 1)
                users[current_peer]["username"] = username
        elif line.strip().startswith("AllowedIPs ="):
            if current_peer:
                users[current_peer]["allowed_ips"] = line.split("=")[1].strip()

    return users

def update_data():
    """Aktualizuje logi JSON i tekstowe na podstawie aktualnych danych `wg`."""
    wg_show = parse_wg_show()
    wg_conf = parse_wg_conf()

    if not wg_show or not wg_conf:
        return

    # Wczytaj lub zainicjalizuj historię JSON
    if os.path.exists(JSON_LOG_PATH):
        with open(JSON_LOG_PATH, "r") as f:
            history = json.load(f)
    else:
        history = {"users": {}}

    for peer, data in wg_conf.items():
        username = data["username"]
        allowed_ips = data["allowed_ips"]
        transfer = wg_show.get(peer, {}).get("transfer", {"received": "0 B", "sent": "0 B"})
        latest_handshake = wg_show.get(peer, {}).get("latest_handshake", None)

        # Aktualizuj dane użytkownika
        user_data = history["users"].get(username, {
            "peer": peer,
            "endpoints": [],
            "allowed_ips": allowed_ips,
            "total_transfer": {"received": "0 B", "sent": "0 B"},
            "last_handshake": None,
            "status": "nieaktywny"
        })

        # Aktualizuj status i handshake
        if latest_handshake:
            user_data["last_handshake"] = latest_handshake
            user_data["status"] = "aktywny"
        else:
            user_data["status"] = "nieaktywny"

        # Aktualizuj dane transferu
        new_received = parse_size(transfer["received"])
        new_sent = parse_size(transfer["sent"])
        old_received = parse_size(user_data["total_transfer"]["received"])
        old_sent = parse_size(user_data["total_transfer"]["sent"])

        # Resetuj jeśli dane zostały wyczyszczone
        if new_received < old_received or new_sent < old_sent:
            new_received += old_received
            new_sent += old_sent

        user_data["total_transfer"] = {
            "received": format_size(new_received),
            "sent": format_size(new_sent)
        }

        # Aktualizuj endpoint
        endpoint = wg_show.get(peer, {}).get("endpoint", None)
        if endpoint and endpoint not in user_data["endpoints"]:
            user_data["endpoints"].append(endpoint)

        # Zapisz do historii
        history["users"][username] = user_data

    # Usuń puste lub duplikowane rekordy
    history["users"] = {
        k: v for k, v in history["users"].items() if k and "Client" not in k
    }

    # Zapisz zaktualizowany JSON
    with open(JSON_LOG_PATH, "w") as f:
        json.dump(history, f, indent=4)

    # Loguj do pliku tekstowego
    with open(TEXT_LOG_PATH, "a") as f:
        for username, user_data in history["users"].items():
            status = user_data["status"]
            transfer = user_data["total_transfer"]
            f.write(f"{datetime.now()}: {username} — {status}. Ruch: {transfer['received']} / {transfer['sent']}\n")

def parse_size(size_str):
    """Parsuje ciąg rozmiaru (np. '4.88 KiB') na bajty."""
    size, unit = size_str.split()
    size = float(size)
    unit = unit.lower()
    multiplier = {
        "b": 1,
        "kib": 1024,
        "mib": 1024**2,
        "gib": 1024**3
    }
    return int(size * multiplier.get(unit, 1))

def format_size(size_bytes):
    """Formatuje rozmiar w bajtach do czytelnego formatu."""
    for unit in ["B", "KiB", "MiB", "GiB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} GiB"

if __name__ == "__main__":
    update_data()
