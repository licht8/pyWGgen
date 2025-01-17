#!/usr/bin/env python3
# modules/manage_users_menu.py
# Module for managing WireGuard users
# Updated 01/14/25

import os
import json
import sys
import subprocess
from modules.utils import get_wireguard_subnet, read_json, write_json
from settings import USER_DB_PATH, SERVER_CONFIG_FILE, WG_CONFIG_DIR, QR_CODE_DIR, SERVER_WG_NIC
from modules.traffic_updater import update_traffic_data
from modules.handshake_updater import update_handshakes

def ensure_directory_exists(filepath):
    """Ensures that the directory for the file exists."""
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_user_records():
    """Loads user data from a JSON file."""
    return read_json(USER_DB_PATH)

def create_user():
    """Creates a new user by invoking main.py."""
    username = input("Enter username: ").strip()
    if not username:
        print("❌ Username cannot be empty.")
        return

    email = input("Enter email (optional): ").strip() or "N/A"
    telegram_id = input("Enter Telegram ID (optional): ").strip() or "N/A"

    try:
        subprocess.run(
            ["python3", os.path.join("main.py"), username, email, telegram_id],
            check=True,
            cwd=os.path.abspath(os.path.dirname(__file__) + "/../")
        )

    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating user: {e}")

def list_users():
    """Displays a list of all users."""
    records = load_user_records()
    if not records:
        print("⚠️ User list is empty.")
        return

    print("\n👤 WireGuard Users:")
    for username, data in records.items():
        allowed_ips = data.get("allowed_ips", "N/A")
        status = data.get("status", "N/A")
        print(f"  - {username}: {allowed_ips} | Status: {status}")

def show_traffic():
    """Retrieves and displays user traffic."""
    try:
        print("\n🔄 Updating user traffic...")
        update_traffic_data(USER_DB_PATH)
        print("✅ User traffic updated.")

        records = load_user_records()
        print("\n📊 User Traffic:")
        for username, data in records.items():
            transfer = data.get("transfer", "N/A")
            total_transfer = data.get("total_transfer", "N/A")
            print(f"  - {username}: {transfer} | Total: {total_transfer}")
    except Exception as e:
        print(f"⚠️ Error retrieving user traffic: {e}")

def show_handshakes():
    """Retrieves and displays information about the last handshakes."""
    try:
        print("\n🔄 Updating last handshake information...")
        update_handshakes(USER_DB_PATH, SERVER_WG_NIC)
        print("✅ Last handshake information updated.")

        records = load_user_records()
        print("\n🤝 Last Handshakes:")
        for username, data in records.items():
            last_handshake = data.get("last_handshake", "Never")
            print(f"  - {username}: Last Handshake: {last_handshake}")
    except Exception as e:
        print(f"⚠️ Error updating handshake information: {e}")

def delete_user():
    """
    Deletes a user from the WireGuard configuration and related files.
    """
    username = input("Enter username to delete: ").strip()
    if not username:
        print("❌ Error: Username cannot be empty.")
        return

    print(f"➡️ Starting deletion of user: '{username}'.")

    if not os.path.exists(USER_DB_PATH):
        print(f"❌ User data file not found: {USER_DB_PATH}")
        return

    try:
        # Load user data
        user_data = read_json(USER_DB_PATH)
        if username not in user_data:
            print(f"❌ User '{username}' does not exist.")
            return

        # Remove user record
        user_data.pop(username)
        write_json(USER_DB_PATH, user_data)
        print(f"📝 User record '{username}' removed from data.")

        # Delete user's configuration file
        wg_config_path = WG_CONFIG_DIR / f"{username}.conf"
        if wg_config_path.exists():
            wg_config_path.unlink()
            print(f"🗑️ Configuration '{wg_config_path}' deleted.")

        # Delete user's QR code
        qr_code_path = QR_CODE_DIR / f"{username}.png"
        if qr_code_path.exists():
            qr_code_path.unlink()
            print(f"🗑️ QR code '{qr_code_path}' deleted.")

        # Extract user's public key
        public_key = extract_public_key(username, SERVER_CONFIG_FILE)
        if not public_key:
            print(f"❌ Public key for user '{username}' not found in WireGuard configuration.")
            return

        # Remove user from WireGuard
        subprocess.run(["sudo", "wg", "set", "wg0", "peer", public_key, "remove"], check=True)
        print(f"🔐 User '{username}' removed from WireGuard.")

        # Update WireGuard configuration
        remove_peer_from_config(public_key, SERVER_CONFIG_FILE, username)
        print(f"✅ WireGuard configuration updated.")

        # Synchronize WireGuard
        sync_command = f'wg syncconf "{SERVER_WG_NIC}" <(wg-quick strip "{SERVER_WG_NIC}")'
        subprocess.run(sync_command, shell=True, check=True, executable='/bin/bash')
        print(f"WireGuard synchronized for interface {SERVER_WG_NIC}")

        print(f"✅ User '{username}' successfully deleted.")
    except Exception as e:
        print(f"⚠️ Error deleting user '{username}': {e}")

def extract_public_key(username, config_path):
    """
    Extracts a user's public key from the WireGuard configuration file.

    Args:
        username (str): The username.
        config_path (str): Path to the WireGuard configuration file.

    Returns:
        str: The user's public key.
    """
    try:
        with open(config_path, "r") as f:
            lines = f.readlines()

        found_username = False
        for line in lines:
            if username in line:
                found_username = True
            elif found_username and line.strip().startswith("PublicKey"):
                return line.split("=", 1)[1].strip()
        return None
    except Exception as e:
        print(f"⚠️ Error finding public key: {e}")
        return None

def remove_peer_from_config(public_key, config_path, client_name):
    """
    Removes the [Peer] section and associated comment from the WireGuard configuration file.

    Args:
        public_key (str): The user's public key.
        config_path (str): Path to the WireGuard configuration file.
        client_name (str): The client name.
    """
    try:
        with open(config_path, "r") as f:
            lines = f.readlines()

        updated_lines = []
        skip_lines = 0

        for line in lines:
            # If the client's comment is found
            if line.strip() == f"### Client {client_name}":
                skip_lines = 5  # Remove 5 lines starting from here
                continue

            # Skip lines related to the removed block
            if skip_lines > 0:
                skip_lines -= 1
                continue

            # Keep other lines
            updated_lines.append(line)

        # Write updated configuration
        with open(config_path, "w") as f:
            f.writelines(updated_lines)
    except Exception as e:
        print(f"⚠️ Error updating configuration: {e}")

def manage_users_menu():
    """User management menu."""
    while True:
        print("\n========== User Management ==========")
        print("1. 🌱 Create User")
        print("2. 🔍 List All Users")
        print("3. ❌ Delete User")
        print("4. 📊 View User Traffic")
        print("5. 🤝 View Last Handshakes")
        print("0. Return to Main Menu")
        print("=====================================")

        choice = input("Select an action: ").strip()
        if choice == "1":
            create_user()
        elif choice == "2":
            list_users()
        elif choice == "3":
            delete_user()
        elif choice == "4":
            show_traffic()
        elif choice == "5":
            show_handshakes()
        elif choice in {"0", "q"}:
            break
        else:
            print("⚠️ Invalid selection. Please try again.")
