#!/usr/bin/env python3
import json
import shutil
from pathlib import Path
from settings import USER_DB_PATH, SERVER_CONFIG_FILE
from modules.main_registration_fields import create_user_record
from modules.qr_generator import generate_qr_code

def get_valid_path(prompt):
    while True:
        path_str = input(prompt).strip()
        path = Path(path_str)
        if path.exists() and path.is_dir():
            return path
        print(f"Error: Directory '{path_str}' does not exist. Please try again.\n")

def find_user_files(username, config_dir, qr_dir):
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
    logs = []
    try:
        config_dir = Path(config_dir_str)
        qr_dir = Path(qr_dir_str)

        if not config_dir.is_dir():
            raise ValueError(f"Config directory not found: {config_dir}")
        if not qr_dir.is_dir():
            raise ValueError(f"QR directory not found: {qr_dir}")

        logs.append("=== 🛠 Starting User Synchronization ===")
        logs.append(f"Config dir: {config_dir}\nQR dir: {qr_dir}\n")

        # Parse server config
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
                _, value = line.split('=', 1)
                public_key = value.strip()
                missing_padding = len(public_key) % 4
                if missing_padding:
                    public_key += '=' * (4 - missing_padding)
                current_user["public_key"] = public_key
            elif line.startswith("PresharedKey ="):
                _, value = line.split('=', 1)
                preshared_key = value.strip()
                missing_padding = len(preshared_key) % 4
                if missing_padding:
                    preshared_key += '=' * (4 - missing_padding)
                current_user["preshared_key"] = preshared_key
            elif line.startswith("AllowedIPs ="):
                current_user["allowed_ips"] = line.split('=', 1)[1].strip()
            elif line == "" and current_user:
                users.append(current_user)
                current_user = {}
        if current_user:
            users.append(current_user)

        # Load existing records
        user_records = {}
        if USER_DB_PATH.exists():
            with open(USER_DB_PATH, "r") as f:
                user_records = json.load(f)

        new_users = 0
        for user in users:
            username = user["username"]
            logs.append(f"Processing: {username}")

            config_path, qr_path = find_user_files(username, config_dir, qr_dir)
            
            # Skip if no files found
            if not config_path and not qr_path:
                logs.append(f"  ❗ Skipping - no config/QR found")
                continue

            target_config = Path(f"user/data/wg_configs/{username}.conf")
            target_qr = Path(f"user/data/qrcodes/{username}.png")
            
            # Create directories if needed
            target_config.parent.mkdir(parents=True, exist_ok=True)
            target_qr.parent.mkdir(parents=True, exist_ok=True)

            # Handle config file
            config_processed = False
            if config_path:
                shutil.copy(config_path, target_config)
                logs.append(f"  ✅ Copied config: {config_path.name}")
                config_processed = True
            else:
                logs.append(f"  ⚠️ No config found")

            # Handle QR code
            qr_processed = False
            if qr_path:
                shutil.copy(qr_path, target_qr)
                logs.append(f"  ✅ Copied QR: {qr_path.name}")
                qr_processed = True
            elif config_processed:
                try:
                    generate_qr_code(target_config.read_text(), str(target_qr))
                    logs.append("  🔄 Generated QR from config")
                    qr_processed = True
                except Exception as e:
                    logs.append(f"  ❗ QR generation failed: {str(e)}")

            # Skip if no files were processed
            if not config_processed and not qr_processed:
                logs.append(f"  ❗ Skipping - no files processed")
                continue

            # Update user records
            if username not in user_records:
                user_record = create_user_record(
                    username=username,
                    address=user.get("allowed_ips", ""),
                    public_key=user.get("public_key", ""),
                    preshared_key=user.get("preshared_key", ""),
                    qr_code_path=str(target_qr) if qr_processed else None
                )
                user_record["config_path"] = str(target_config) if config_processed else None
                user_records[username] = user_record
                new_users += 1

        # Save updated database
        with open(USER_DB_PATH, "w") as f:
            json.dump(user_records, f, indent=4)

        logs.append(f"\n✅ Sync complete! New users: {new_users}")
        return True, "\n".join(logs)

    except Exception as e:
        logs.append(f"❌ Critical error: {str(e)}")
        return False, "\n".join(logs)

def sync_users_from_config():
    try:
        print("\n=== 🔄 User Sync (Console Mode) ===")
        config_dir = get_valid_path("Path to client configs: ")
        qr_dir = get_valid_path("Path to QR codes: ")
        
        success, log = sync_users_from_config_paths(str(config_dir), str(qr_dir))
        print(log)
        return success
        
    except KeyboardInterrupt:
        print("\n🚫 Operation cancelled by user")
        return False

if __name__ == "__main__":
    sync_users_from_config()