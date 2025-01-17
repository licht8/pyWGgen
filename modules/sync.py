#!/usr/bin/env python3
# modules/sync.py
# Module for syncing WireGuard users with the project

import json
from pathlib import Path
from settings import USER_DB_PATH, SERVER_CONFIG_FILE
from modules.main_registration_fields import create_user_record

def sync_users_from_config():
    """
    Synchronizes users from the WireGuard configuration file with user_records.json.
    """
    try:
        # Read the WireGuard configuration file
        with open(SERVER_CONFIG_FILE, "r") as f:
            config_lines = f.readlines()

        # Parse users from the configuration
        users_in_config = []
        current_user = {}

        for line in config_lines:
            stripped_line = line.strip()

            # Look for the comment ### Client <name>
            if stripped_line.startswith("### Client"):
                if current_user:
                    users_in_config.append(current_user)  # Save the previous user
                current_user = {"username": stripped_line.split("### Client")[1].strip()}

            # Extract PublicKey, PresharedKey, and AllowedIPs
            elif stripped_line.startswith("PublicKey ="):
                current_user["public_key"] = stripped_line.split("PublicKey =")[1].strip()
            elif stripped_line.startswith("PresharedKey ="):
                current_user["preshared_key"] = stripped_line.split("PresharedKey =")[1].strip()
            elif stripped_line.startswith("AllowedIPs ="):
                current_user["allowed_ips"] = stripped_line.split("AllowedIPs =")[1].strip()

            # End of the [Peer] block
            elif stripped_line == "" and current_user:
                users_in_config.append(current_user)
                current_user = {}

        # Add the last user, if any
        if current_user:
            users_in_config.append(current_user)

        print(f"[DEBUG] Users in config: {users_in_config}")

        # Read the current records in user_records.json
        user_records = {}
        if Path(USER_DB_PATH).exists():
            with open(USER_DB_PATH, "r") as f:
                user_records = json.load(f)

        # Sync users
        new_users = 0
        for user in users_in_config:
            username = user["username"]
            if username not in user_records:
                # Create a new user using create_user_record
                user_record = create_user_record(
                    username=username,
                    address=user["allowed_ips"],
                    public_key=user["public_key"],
                    preshared_key=user["preshared_key"],
                    qr_code_path=f"user/data/qrcodes/{username}.png"  # Path to the QR code
                )
                user_records[username] = user_record
                new_users += 1

        # Save the updated user_records.json
        with open(USER_DB_PATH, "w") as f:
            json.dump(user_records, f, indent=4)

        print(f"[INFO] Sync complete. {new_users} new user(s) added.")
        return f"Sync complete. {new_users} new user(s) added."

    except Exception as e:
        print(f"[ERROR] Failed to sync users: {e}")
        return f"Failed to sync users: {e}"
