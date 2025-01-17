#!/usr/bin/env python3
# gradio_admin/functions/block_user.py

import json
import subprocess  # For managing VPN via system commands
from settings import USER_DB_PATH, SERVER_CONFIG_FILE  # Paths to JSON and WireGuard configuration
from settings import SERVER_WG_NIC

def load_user_records():
    """Loads user records from JSON."""
    try:
        with open(USER_DB_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"[ERROR] Failed to load user records: {e}")
        return {}

def save_user_records(records):
    """Saves user records to JSON."""
    try:
        with open(USER_DB_PATH, "w") as f:
            json.dump(records, f, indent=4)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save user records: {e}")
        return False

def block_user(username):
    """
    Blocks a user:
    1. Updates the status in JSON to 'blocked'.
    2. Removes the user from the WireGuard configuration.
    """
    records = load_user_records()
    if username not in records:
        return False, f"User '{username}' not found."

    # Update status in JSON
    records[username]["status"] = "blocked"
    if not save_user_records(records):
        return False, f"Failed to update JSON for user '{username}'."

    # Remove user from configuration
    if not update_wireguard_config(username, block=True):
        return False, f"Failed to block VPN access for user '{username}'."

    return True, f"User '{username}' has been blocked and VPN access revoked."

def unblock_user(username):
    """
    Unblocks a user:
    1. Updates the status in JSON to 'active'.
    2. Restores the user in the WireGuard configuration.
    """
    records = load_user_records()
    if username not in records:
        return False, f"User '{username}' not found."

    # Update status in JSON
    records[username]["status"] = "active"
    if not save_user_records(records):
        return False, f"Failed to update JSON for user '{username}'."

    # Restore user in configuration
    if not update_wireguard_config(username, block=False):
        return False, f"Failed to restore VPN access for user '{username}'."

    return True, f"User '{username}' has been unblocked and VPN access restored."

def update_wireguard_config(username, block=True):
    """
    Updates the WireGuard configuration file:
    1. If block=True, comments out the entire [Peer] block related to the user.
    2. If block=False, restores the [Peer] block.
    """
    try:
        with open(SERVER_CONFIG_FILE, "r") as f:
            config_lines = f.readlines()

        updated_lines = []
        in_peer_block = False
        peer_belongs_to_user = False

        for idx, line in enumerate(config_lines):
            stripped_line = line.strip()

            # Identify the user via the comment ### Client <username>
            if stripped_line == f"### Client {username}":
                in_peer_block = True
                peer_belongs_to_user = True
                updated_lines.append(line)  # Add the comment as is
                continue

            # Process the [Peer] block if it belongs to the user
            if in_peer_block and peer_belongs_to_user:
                if block:
                    if not line.startswith("#"):
                        updated_lines.append(f"# {line}")  # Comment out the line
                    else:
                        updated_lines.append(line)  # Already commented
                else:
                    if line.startswith("# "):
                        updated_lines.append(line[2:])  # Remove the comment
                    else:
                        updated_lines.append(line)  # Already uncommented

                # End of [Peer] block - empty line
                if stripped_line == "":
                    in_peer_block = False
                    peer_belongs_to_user = False
                continue

            # All other lines
            updated_lines.append(line)

        # Save the updated configuration file
        with open(SERVER_CONFIG_FILE, "w") as f:
            f.writelines(updated_lines)

        # Sync WireGuard
        sync_command = f'wg syncconf "{SERVER_WG_NIC}" <(wg-quick strip "{SERVER_WG_NIC}")'
        subprocess.run(sync_command, shell=True, check=True, executable='/bin/bash')
        print(f"WireGuard synced for interface {SERVER_WG_NIC}")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to update WireGuard config: {e}")
        return False
