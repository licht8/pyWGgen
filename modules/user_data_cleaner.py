#!/usr/bin/env python3
# modules/user_data_cleaner.py
# Module for selective cleaning of user data

import os
import shutil
import subprocess
from settings import SERVER_WG_NIC  # SERVER_WG_NIC from the params file
from settings import USER_DB_PATH  # User database
from settings import SERVER_CONFIG_FILE
from settings import SERVER_BACKUP_CONFIG_FILE
from settings import WG_CONFIG_DIR, QR_CODE_DIR

WG_USERS_JSON = "logs/wg_users.json"

def confirm_action(message):
    """User confirmation for an action."""
    while True:
        choice = input(f"{message} (y/n): ").strip().lower()
        if choice in {"y", "n"}:
            return choice == "y"
        print("⚠️ Please enter 'y' to confirm or 'n' to cancel.")

def clean_user_data():
    """Selective cleaning of user data with confirmation."""
    try:
        # Clean user_records.json
        if os.path.exists(USER_DB_PATH) and confirm_action("🧹 Clean the user_records.json file?"):
            os.remove(USER_DB_PATH)
            print(f"✅ {USER_DB_PATH} cleaned.")

        # Clean wg_users.json
        if os.path.exists(WG_USERS_JSON) and confirm_action("🧹 Clean the wg_users.json file?"):
            os.remove(WG_USERS_JSON)
            print(f"✅ {WG_USERS_JSON} cleaned.")

        # Clean WireGuard configuration
        if os.path.exists(SERVER_CONFIG_FILE) and confirm_action("🧹 Clean the WireGuard configuration file (remove all ### Client and [Peer])?"):
            # Create a backup
            shutil.copy2(SERVER_CONFIG_FILE, SERVER_BACKUP_CONFIG_FILE)
            print(f"✅ Backup created: {SERVER_BACKUP_CONFIG_FILE}")

            # Clean the configuration
            with open(SERVER_CONFIG_FILE, "r") as wg_file:
                lines = wg_file.readlines()

            # New content without ### Client blocks and associated [Peer]
            cleaned_lines = []
            inside_client_block = False

            for line in lines:
                stripped_line = line.strip()
                if stripped_line.startswith("### Client"):
                    inside_client_block = True
                elif inside_client_block and stripped_line == "":
                    # End of block, toggle flag
                    inside_client_block = False
                elif not inside_client_block:
                    cleaned_lines.append(line)

            with open(SERVER_CONFIG_FILE, "w") as wg_file:
                wg_file.writelines(cleaned_lines)
            print(f"✅ WireGuard configuration cleaned.")

        # Clean user configuration files
        if os.path.exists(WG_CONFIG_DIR) and confirm_action("🧹 Clean all user configuration files?"):
            for config_file in os.listdir(WG_CONFIG_DIR):
                file_path = os.path.join(WG_CONFIG_DIR, config_file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print(f"✅ User configuration files in {WG_CONFIG_DIR} cleaned.")

        # Clean user QR codes
        if os.path.exists(QR_CODE_DIR) and confirm_action("🧹 Clean all user QR codes?"):
            for qr_code_file in os.listdir(QR_CODE_DIR):
                file_path = os.path.join(QR_CODE_DIR, qr_code_file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print(f"✅ User QR codes in {QR_CODE_DIR} cleaned.")

        # Sync WireGuard
        sync_command = f'wg syncconf "{SERVER_WG_NIC}" <(wg-quick strip "{SERVER_WG_NIC}")'
        subprocess.run(sync_command, shell=True, check=True, executable='/bin/bash')
        print(f"WireGuard synchronized for interface {SERVER_WG_NIC}")

        print("🎉 Cleaning complete. All data processed.")

    except Exception as e:
        print(f"❌ Error during data cleaning: {e}")
