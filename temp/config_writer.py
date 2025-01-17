import os

def add_user_to_server_config(config_file, nickname, public_key, preshared_key, allowed_ips):
    with open(config_file, 'a') as file:
        file.write(f"\n### Client {nickname}\n")
        file.write(f"[Peer]\n")
        file.write(f"PublicKey = {public_key}\n")
        file.write(f"PresharedKey = {preshared_key}\n")
        file.write(f"AllowedIPs = {allowed_ips}\n")

def remove_user_from_server_config(config_file, nickname):
    if not os.path.exists(config_file):
        return
    
    with open(config_file, 'r') as file:
        lines = file.readlines()
    
    with open(config_file, 'w') as file:
        skip = False
        for line in lines:
            if line.strip().startswith(f"### Client {nickname}"):
                skip = True
            if skip and line.strip() == "":
                skip = False
                continue
            if not skip:
                file.write(line)
