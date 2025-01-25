#!/usr/bin/env python3
import json
import shutil
from pathlib import Path
from settings import USER_DB_PATH, SERVER_CONFIG_FILE
from modules.main_registration_fields import create_user_record
from modules.qr_generator import generate_qr_code

def get_valid_path(prompt):
    """
    Continuously prompts the user for a path until a valid (existing) directory is provided.
    Returns a Path object.
    """
    while True:
        path_str = input(prompt).strip()
        path = Path(path_str)
        if path.exists() and path.is_dir():
            return path
        print(f"Error: Directory '{path_str}' does not exist or is inaccessible. Please try again.\n")

def find_user_files(username, config_dir, qr_dir):
    """
    Searches for the user's config and QR code files in the specified directories.
    Returns a tuple (config_path, qr_path) which may be None if not found.
    """
    config_path = next(
        (f for ext in ['.conf', '.txt']
         if (f := config_dir / f"{username}{ext}").exists()), 
        None
    )
    qr_path = next(
        (f for ext in ['.png', '.jpg', '.svg']
         if (f := qr_dir / f"{username}{ext}").exists()), 
        None
    )
    return config_path, qr_path

def sync_users_from_config_paths(config_dir_str: str, qr_dir_str: str):
    """
    The main synchronization logic. 
    Accepts directory paths (as strings) for config files and QR codes.

    Returns a tuple (success: bool, logs: str):
      - success indicates whether the operation was successful
      - logs is a multi-line string of the actions taken
    """
    logs = []
    try:
        config_dir = Path(config_dir_str)
        qr_dir = Path(qr_dir_str)

        # Verify that the provided paths are valid directories
        if not config_dir.is_dir():
            raise ValueError(f"Config directory not found: {config_dir}")
        if not qr_dir.is_dir():
            raise ValueError(f"QR code directory not found: {qr_dir}")

        logs.append("=== 🛠 Starting User Synchronization ===")
        logs.append(f"Config directory: {config_dir}")
        logs.append(f"QR code directory: {qr_dir}\n")

        # Step 1: Parse the server config file
        with open(SERVER_CONFIG_FILE, "r") as f:
            config_content = f.read()

        users = []
        current_user = {}

        for line in config_content.split('\n'):
            line = line.strip()
            if line.startswith("### Client"):
                if current_user:
                    users.append(current_user)
                current_user = {"username": line.split("### Client")[1].strip()}
            elif line.startswith("PublicKey ="):
                current_user["public_key"] = line.split("=")[1].strip()
            elif line.startswith("PresharedKey ="):
                current_user["preshared_key"] = line.split("=")[1].strip()
            elif line.startswith("AllowedIPs ="):
                current_user["allowed_ips"] = line.split("=")[1].strip()
            elif line == "" and current_user:
                # user definition ended
                users.append(current_user)
                current_user = {}

        # If there's a user definition being built at the end, add it as well
        if current_user:
            users.append(current_user)

        # Step 2: Load existing user records (if any)
        user_records = {}
        if Path(USER_DB_PATH).exists():
            with open(USER_DB_PATH, "r") as f:
                user_records = json.load(f)

        # Step 3: Process each user found in the server config
        new_users = 0
        for user in users:
            username = user["username"]
            logs.append(f"Processing user: {username}")

            # Locate user's config and QR in the provided directories
            config_path, qr_path = find_user_files(username, config_dir, qr_dir)
            
            # The target paths where we'll copy/generate the files
            target_config = Path(f"user/data/wg_configs/{username}.conf")
            target_qr = Path(f"user/data/qrcodes/{username}.png")

            # Create any missing directories
            target_config.parent.mkdir(parents=True, exist_ok=True)
            target_qr.parent.mkdir(parents=True, exist_ok=True)

            # Copy or create config file
            if config_path:
                shutil.copy(config_path, target_config)
                logs.append(f"  ✅ Copied config: {config_path} → {target_config}")
            else:
                target_config.touch()
                logs.append(f"  ⚠️ No config found for {username}! Created an empty file.")

            # Copy or generate QR code
            if qr_path:
                shutil.copy(qr_path, target_qr)
                logs.append(f"  ✅ Copied QR code: {qr_path} → {target_qr}")
            elif config_path:
                qr_text = target_config.read_text()
                generate_qr_code(qr_text, str(target_qr))
                logs.append(f"  🔄 Generated QR code from the config.")
            else:
                logs.append(f"  ⚠️ No QR code generated (no config available).")

            # Update user records
            if username not in user_records:
                # We only need create_user_record if the user is new
                user_record = create_user_record(
                    username=username,
                    address=user.get("allowed_ips", ""),
                    public_key=user.get("public_key", ""),
                    preshared_key=user.get("preshared_key", ""),
                    qr_code_path=str(target_qr)  # so it gets stored in the record
                )
                user_record["config_path"] = str(target_config)
                user_record["qr_code_path"] = str(target_qr) if target_qr.exists() else None

                user_records[username] = user_record
                new_users += 1

        # Step 4: Save updates to the user database
        with open(USER_DB_PATH, "w") as f:
            json.dump(user_records, f, indent=4)

        logs.append(f"\n🎉 Synchronization complete! New users added: {new_users}")
        return True, "\n".join(logs)

    except Exception as e:
        error_msg = f"❌ Synchronization error: {str(e)}"
        logs.append(error_msg)
        return False, "\n".join(logs)


def sync_users_from_config():
    """
    The old 'console-based' function: asks the user for directories 
    via input() and then calls sync_users_from_config_paths.
    It prints the resulting logs to the console.
    """
    try:
        print("\n=== 🛠 USER SYNCHRONIZATION (console mode) ===")
        config_dir = get_valid_path("Client configs directory: ")
        qr_dir = get_valid_path("QR codes directory: ")

        success, log = sync_users_from_config_paths(str(config_dir), str(qr_dir))
        print(log)  # Print the logs in the console

        return success
    except KeyboardInterrupt:
        print("\nSynchronization aborted by user.")
        return False


if __name__ == "__main__":
    # If you run `python sync.py` directly, it will use the interactive console mode.
    sync_users_from_config()
