#!/usr/bin/env python3
# modules/handshake_updater.py

import os
import json
import subprocess
from datetime import datetime
from settings import USER_DB_PATH, SERVER_WG_NIC

def get_latest_handshakes(interface):
    """
    Retrieves information about the latest handshakes of WireGuard users.
    :param interface: Name of the WireGuard interface.
    :return: Dictionary {public_key: last_handshake}.
    """
    try:
        output = subprocess.check_output(["wg", "show", interface, "latest-handshakes"], text=True)
        lines = output.strip().split("\n")
        handshakes = {}

        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                public_key = parts[0]
                timestamp = int(parts[1])
                handshakes[public_key] = convert_handshake_timestamp(timestamp)

        return handshakes
    except Exception as e:
        print(f"Error while retrieving handshake information: {e}")
        return {}

def convert_handshake_timestamp(timestamp):
    """
    Converts a Unix timestamp into a readable format.
    :param timestamp: Timestamp (Unix timestamp).
    :return: Readable date and time string in UTC format or 'Never' if no handshake was established (timestamp equals 0).
    """
    if timestamp == 0:
        return "Never"
    return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")

def update_handshakes(user_records_path, interface):
    """
    Updates information about the latest handshakes of users in user_records.json.
    :param user_records_path: Path to the user_records.json file.
    :param interface: Name of the WireGuard interface.
    """
    if not os.path.exists(user_records_path):
        print(f"File {user_records_path} not found.")
        return

    with open(user_records_path, "r") as f:
        user_records = json.load(f)

    handshakes = get_latest_handshakes(interface)

    for username, user_data in user_records.items():
        public_key = user_data.get("public_key")
        if public_key in handshakes:
            user_data["last_handshake"] = handshakes[public_key]

    with open(user_records_path, "w") as f:
        json.dump(user_records, f, indent=4)

    print("Latest handshake information successfully updated.")

if __name__ == "__main__":
    # Update handshakes for users
    update_handshakes(USER_DB_PATH, SERVER_WG_NIC)
