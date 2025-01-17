#!/usr/bin/env python3
# modules/traffic_updater.py

import json
import os
import subprocess
from settings import SERVER_WG_NIC  # Import WireGuard interface from settings
from settings import USER_DB_PATH

def update_traffic_data(user_records_path):
    """
    Updates user traffic data, recording the same values for transfer and total_transfer in user_records.json.
    """
    if not os.path.exists(USER_DB_PATH):
        print(f"File {USER_DB_PATH} not found.")
        return

    # Load user data
    with open(USER_DB_PATH, "r") as f:
        user_records = json.load(f)

    try:
        # Retrieve traffic data from WireGuard
        output = subprocess.check_output(["wg", "show", SERVER_WG_NIC, "transfer"], text=True)
        lines = output.strip().split("\n")

        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                public_key = parts[0]
                received = int(parts[1])  # Current received data
                sent = int(parts[2])

                # Find the user by public_key
                for username, user_data in user_records.items():
                    if user_data.get("public_key") == public_key:
                        # Update the transfer field
                        transfer_str = f"{received / (1024 ** 2):.2f} MiB received, {sent / (1024 ** 2):.2f} MiB sent"
                        user_data["transfer"] = transfer_str
                        user_data["total_transfer"] = transfer_str  # Duplicate the value
                        break

    except Exception as e:
        print(f"Error updating traffic data: {e}")
        return

    # Save updated data
    with open(USER_DB_PATH, "w") as f:
        json.dump(user_records, f, indent=4)
