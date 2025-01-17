#!/usr/bin/env python3
# delete_user.py
# Script for deleting users in the wg_qr_generator project

import os
import subprocess
from datetime import datetime
from modules.utils import read_json, write_json, get_wireguard_config_path
from settings import WG_CONFIG_DIR, QR_CODE_DIR, SERVER_WG_NIC

# Logging function (similar to log_debug)
def log_debug(message):
    """
    Simple function to output messages to the console with timestamp in milliseconds.
    :param message: Message to output.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]  # Keep milliseconds
    print(f"{timestamp} - DEBUG    ℹ️  {message}")

def delete_user(username):
    """
    Deletes a user from the WireGuard configuration and associated files.
    :param username: The username to delete.
    :return: Message about the result of the operation.
    """
    log_debug("---------- 🔥 User deletion process activated ----------")

    base_dir = os.getcwd()
    user_records_path = os.path.join(base_dir, "user", "data", "user_records.json")
    wg_config_path = get_wireguard_config_path()

    log_debug(f"➡️ Starting deletion of user: '{username}'.")

    if not os.path.exists(user_records_path):
        log_debug(f"❌ User data file not found: {user_records_path}")
        log_debug("---------- 🔥 User deletion process finished ---------------\n")
        return "❌ Error: User data file is missing."

    try:
        # Load user data
        user_data = read_json(user_records_path)
        log_debug(f"📂 User data successfully loaded.")

        if username not in user_data:
            log_debug(f"❌ User '{username}' not found in data.")
            log_debug("---------- 🔥 User deletion process finished ---------------\n")
            return f"❌ User '{username}' does not exist."

        # Remove user record from user_records.json
        user_info = user_data.pop(username)
        user_info["removed_at"] = datetime.now().isoformat()
        write_json(user_records_path, user_data)
        log_debug(f"📝 User record '{username}' removed from data.")

        # Delete user's configuration file
        wg_config_file = os.path.join(WG_CONFIG_DIR, f"{username}.conf")
        if os.path.exists(wg_config_file):
            os.remove(wg_config_file)
            log_debug(f"🗑️ User's configuration file '{wg_config_file}' deleted.")

        # Delete user's QR code
        qr_code_file = os.path.join(QR_CODE_DIR, f"{username}.png")
        if os.path.exists(qr_code_file):
            os.remove(qr_code_file)
            log_debug(f"🗑️ User's QR code '{qr_code_file}' deleted.")

        # Extract user's public key
        public_key = extract_public_key(username, wg_config_path)
        if not public_key:
            log_debug(f"❌ Public key for user '{username}' not found in WireGuard configuration.")
            log_debug("---------- 🔥 User deletion process finished ---------------\n")
            return f"❌ Public key for user '{username}' is missing."

        # Remove user from WireGuard
        subprocess.run(["sudo", "wg", "set", "wg0", "peer", public_key, "remove"], check=True)
        log_debug(f"🔐 User '{username}' removed from WireGuard.")

        # Update WireGuard configuration
        remove_peer_from_config(public_key, wg_config_path, username)
        log_debug(f"✅ WireGuard configuration successfully updated.")

        # Sync WireGuard
        sync_command = f'wg syncconf "{SERVER_WG_NIC}" <(wg-quick strip "{SERVER_WG_NIC}")'
        subprocess.run(sync_command, shell=True, check=True, executable='/bin/bash')
        print(f"WireGuard synced for interface {SERVER_WG_NIC}")

        log_debug("---------- 🔥 User deletion process finished ---------------\n")
        return f"✅ User '{username}' successfully deleted."
    except Exception as e:
        log_debug(f"⚠️ Error deleting user '{username}': {str(e)}")
        log_debug("---------- 🔥 User deletion process finished ---------------\n")
        return f"❌ Error deleting user '{username}': {str(e)}"

def extract_public_key(username, config_path):
    """
    Extracts the public key of a user from the WireGuard configuration.
    :param username: Username.
    :param config_path: Path to the WireGuard configuration file.
    :return: User's public key.
    """
    log_debug(f"🔍 Searching for public key for user '{username}' in {config_path}.")
    try:
        with open(config_path, "r") as f:
            lines = f.readlines()

        found_username = False
        for line in lines:
            if username in line:
                found_username = True
            elif found_username and line.strip().startswith("PublicKey"):
                public_key = line.split("=", 1)[1].strip()
                log_debug(f"🔑 Found public key for '{username}': {public_key}")
                return public_key
        log_debug(f"❌ Public key for '{username}' not found.")
        return None
    except Exception as e:
        log_debug(f"⚠️ Error finding public key: {str(e)}")
        return None

def remove_peer_from_config(public_key, config_path, client_name):
    """
    Removes the [Peer] block and associated comment from the WireGuard configuration file.
    Deletes the comment and 4 lines starting from it.
    :param public_key: User's public key.
    :param config_path: Path to the WireGuard configuration file.
    :param client_name: Client name.
    """
    log_debug(f"🛠️ Removing configuration for user '{client_name}' from {config_path}.")

    try:
        with open(config_path, "r") as f:
            lines = f.readlines()

        updated_lines = []
        skip_lines = 0  # Line skip counter

        for i, line in enumerate(lines):
            # If client comment is found
            if line.strip() == f"### Client {client_name}":
                log_debug(f"📌 Found block for '{client_name}' on line {i}. Removing...")
                skip_lines = 5  # Skip 5 lines starting from here
                continue

            # Skip lines related to the removed block
            if skip_lines > 0:
                log_debug(f"⏩ Skipping line {i}: {line.strip()}")
                skip_lines -= 1
                continue

            # Save remaining lines
            updated_lines.append(line)

        # Write updated configuration
        with open(config_path, "w") as f:
            f.writelines(updated_lines)

        log_debug(f"✅ Configuration for user '{client_name}' removed.")
    except Exception as e:
        log_debug(f"⚠️ Error updating configuration: {str(e)}")
