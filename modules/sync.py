#!/usr/bin/env python3
import json
import shutil
from pathlib import Path
from settings import USER_DB_PATH, SERVER_CONFIG_FILE
from modules.main_registration_fields import create_user_record
from modules.qr_generator import generate_qr_code

def get_valid_path(prompt):
    """Requests a path from the user until a valid directory is obtained"""
    while True:
        path = Path(input(prompt).strip())
        if path.exists() and path.is_dir():
            return path
        print(f"Error: Directory '{path}' does not exist or is inaccessible. Please try again.\n")

def find_user_files(username, config_dir, qr_dir):
    """Searches for user files in specified directories"""
    # Search for config
    config_path = next(
        (f for ext in ['.conf', '.txt'] 
         if (f := config_dir / f"{username}{ext}").exists()), None
    )
    
    # Search for QR code
    qr_path = next(
        (f for ext in ['.png', '.jpg', '.svg'] 
         if (f := qr_dir / f"{username}{ext}").exists()), None
    )
    
    return config_path, qr_path

def sync_users_from_config():
    """Main synchronization function with interactive input"""
    try:
        # Step 1: Request paths from user
        print("\n=== 🛠 USER SYNCHRONIZATION ===")
        print("Specify paths to existing files:")
        
        config_dir = get_valid_path("Client configs directory: ")
        qr_dir = get_valid_path("QR codes directory: ")

        # Step 2: Parse server config
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
                users.append(current_user)
                current_user = {}

        if current_user:
            users.append(current_user)

        # Step 3: Process users
        user_records = {}
        if Path(USER_DB_PATH).exists():
            with open(USER_DB_PATH, "r") as f:
                user_records = json.load(f)

        new_users = 0
        for user in users:
            username = user["username"]
            print(f"\n🔍 Processing user: {username}")
            
            # Find files
            config_path, qr_path = find_user_files(username, config_dir, qr_dir)
            
            # Project paths
            target_config = Path(f"user/data/wg_configs/{username}.conf")
            target_qr = Path(f"user/data/qrcodes/{username}.png")
            
            # Create directories if missing
            target_config.parent.mkdir(parents=True, exist_ok=True)
            target_qr.parent.mkdir(parents=True, exist_ok=True)

            # Copy config
            if config_path:
                shutil.copy(config_path, target_config)
                print(f"✅ Config copied: {config_path} → {target_config}")
            else:
                print(f"⚠️ Config for {username} not found! Created empty file.")
                target_config.touch()
                
            # Handle QR code
            if qr_path:
                shutil.copy(qr_path, target_qr)
                print(f"✅ QR code copied: {qr_path} → {target_qr}")
            elif config_path:
                generate_qr_code(target_config.read_text(), str(target_qr))
                print(f"🔄 QR code generated from config")
            else:
                print(f"⚠️ QR code for {username} not created (missing config)")

            # Update user records
            if username not in user_records:
                # Create base record
                user_record = create_user_record(
                    username=username,
                    address=user["allowed_ips"],
                    public_key=user["public_key"],
                    preshared_key=user["preshared_key"],
                    qr_code_path=f"user/data/qrcodes/{username}.png"
                )
                
                # Add additional fields
                user_record.update({
                    "config_path": str(target_config),
                    "qr_code_path": str(target_qr) if target_qr.exists() else None
                })
                
                user_records[username] = user_record
                new_users += 1

        # Save data
        with open(USER_DB_PATH, "w") as f:
            json.dump(user_records, f, indent=4)

        print(f"\n🎉 Synchronization complete! New users added: {new_users}")
        return True

    except Exception as e:
        print(f"\n❌ Critical error: {str(e)}")
        return False

if __name__ == "__main__":
    sync_users_from_config()