#!/usr/bin/env python3
# main.py
## Version: 1.0
## Main script for creating WireGuard users
##
## This script automatically generates configurations for new users,
## including unique keys, IP address, and QR code. The script calculates the subnet
## based on the server's IP address (SERVER_WG_IPV4) and restarts the WireGuard interface.

import sys
import os
import json
import ipaddress
from datetime import datetime
import settings
from modules.config import load_params
from modules.keygen import generate_private_key, generate_public_key, generate_preshared_key
from modules.directory_setup import setup_directories
from modules.client_config import create_client_config
from modules.main_registration_fields import create_user_record  # Import of the new function
import subprocess
import logging
import qrcode
import tempfile

# Logger setup
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)-8s %(message)s",
    handlers=[logging.StreamHandler()]
)

DEBUG_EMOJI = "🐛"
INFO_EMOJI = "ℹ️"
WARNING_EMOJI = "⚠️"
ERROR_EMOJI = "❌"
WG_EMOJI = "🌐"
FIREWALL_EMOJI = "🛡️"

class EmojiLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        if kwargs.get('level', logging.INFO) == logging.DEBUG:
            msg = f"{DEBUG_EMOJI}  {msg}"
        elif kwargs.get('level', logging.INFO) == logging.INFO:
            msg = f"{INFO_EMOJI}  {msg}"
        elif kwargs.get('level', logging.INFO) == logging.WARNING:
            msg = f"{WARNING_EMOJI}  {msg}"
        elif kwargs.get('level', logging.INFO) == logging.ERROR:
            msg = f"{ERROR_EMOJI}  {msg}"
        return msg, kwargs

logger = EmojiLoggerAdapter(logging.getLogger(__name__), {})

def calculate_subnet(server_wg_ipv4, default_subnet="10.66.66.0/24"):
    """
    Calculates the subnet based on the WireGuard server's IP address.
    :param server_wg_ipv4: WireGuard server IP address.
    :param default_subnet: Default subnet.
    :return: Subnet in CIDR format (e.g., '10.66.66.0/24').
    """
    try:
        ip = ipaddress.ip_interface(f"{server_wg_ipv4}/24")
        subnet = str(ip.network)
        logger.debug(f"Subnet calculated based on SERVER_WG_IPV4: {subnet}")
        return subnet
    except ValueError as e:
        logger.warning(f"Error calculating subnet: {e}. Using default value: {default_subnet}")
        return default_subnet

def generate_next_ip(config_file, subnet="10.66.66.0/24"):
    """
    Generates the next available IP address in the subnet.
    :param config_file: Path to the WireGuard configuration file.
    :param subnet: Subnet to search for available IPs.
    :return: Next available IP address.
    """
    logger.debug(f"Searching for a free IP address in subnet {subnet}.")
    existing_ips = []
    if os.path.exists(config_file):
        logger.debug(f"Reading existing IP addresses from file {config_file}.")
        with open(config_file, "r") as f:
            for line in f:
                if line.strip().startswith("AllowedIPs"):
                    ip = line.split("=")[1].strip().split("/")[0]
                    existing_ips.append(ip)
    network = ipaddress.ip_network(subnet)
    for ip in network.hosts():
        ip_str = str(ip)
        if ip_str not in existing_ips and not ip_str.endswith(".0") and not ip_str.endswith(".1") and not ip_str.endswith(".255"):
            logger.debug(f"Free IP address found: {ip_str}")
            return ip_str
    logger.error("No available IP addresses in the specified subnet.")
    raise ValueError("No available IP addresses in the specified subnet.")

def generate_qr_code(data, output_path):
    """
    Generates a QR code based on the configuration data.
    :param data: WireGuard configuration text.
    :param output_path: Path to save the QR code image.
    """
    logger.debug(f"Generating QR code for data with length {len(data)} characters.")
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)

    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        raise

def load_existing_users():
    """
    Loads the list of existing users from the database.
    """
    user_records_path = os.path.join("user", "data", "user_records.json")
    logger.debug(f"Loading user database from {user_records_path}")
    if os.path.exists(user_records_path):
        with open(user_records_path, "r", encoding="utf-8") as file:
            try:
                user_data = json.load(file)
                logger.info(f"Successfully loaded {len(user_data)} users.")
                return {user.lower(): user_data[user] for user in user_data}  # Normalize names
            except json.JSONDecodeError as e:
                logger.warning(f"Error reading database: {e}. Returning an empty database.")
                return {}
    logger.warning(f"User database file {user_records_path} not found.")
    return {}

def is_user_in_server_config(nickname, config_file):
    """
    Checks if the user exists in the server configuration.
    """
    nickname_lower = nickname.lower()
    logger.debug(f"Checking if user {nickname} exists in configuration {config_file}.")
    try:
        with open(config_file, "r") as file:
            for line in file:
                if nickname_lower in line.lower():
                    logger.info(f"User {nickname} found in the server configuration.")
                    return True
    except FileNotFoundError:
        logger.warning(f"Configuration file {config_file} not found.")
    return False

'''
def restart_wireguard(interface="wg0"):
    """
    Restarts WireGuard and displays its status.
    """
    try:
        logger.info(f"Restarting WireGuard interface: {interface}")
        subprocess.run(["sudo", "systemctl", "restart", f"wg-quick@{interface}"], check=True)
        logger.info(f"{WG_EMOJI} WireGuard interface {interface} successfully restarted.")

        # Retrieve WireGuard status
        wg_status = subprocess.check_output(["sudo", "systemctl", "status", f"wg-quick@{interface}"]).decode()
        for line in wg_status.splitlines():
            if "Active:" in line:
                logger.info(f"{WG_EMOJI} WireGuard status: {line.strip()}")

        # Display firewall status
        firewall_status = subprocess.check_output(["sudo", "firewall-cmd", "--list-ports"]).decode()
        for line in firewall_status.splitlines():
            logger.info(f"{FIREWALL_EMOJI} Firewall status: {line.strip()}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error restarting WireGuard: {e}")
'''

def add_user_to_server_config(config_file, nickname, public_key, preshared_key, allowed_ips):
    with open(config_file, 'a') as file:
        file.write(f"\n### Client {nickname}\n")
        file.write(f"[Peer]\n")
        file.write(f"PublicKey = {public_key}\n")
        file.write(f"PresharedKey = {preshared_key}\n")
        file.write(f"AllowedIPs = {allowed_ips}\n")

def generate_config(nickname, params, config_file, email="N/A", telegram_id="N/A"):
    """
    Generates the user's configuration and QR code.
    """
    logger.info("+--------- Process 🌱 User Creation Activated ---------+")
    try:
        logger.info(f"{INFO_EMOJI} Starting configuration generation for user: {nickname}")
        
        # Check for SERVER_PUB_IP
        server_public_key = params['SERVER_PUB_KEY']
        if not params.get('SERVER_PUB_IP'):
            raise ValueError("SERVER_PUB_IP parameter is missing. Check the configuration file.")
        
        endpoint = f"{params['SERVER_PUB_IP']}:{params['SERVER_PORT']}"
        dns_servers = f"{params['CLIENT_DNS_1']},{params['CLIENT_DNS_2']}"

        private_key = generate_private_key()
        logger.debug(f"{DEBUG_EMOJI} Private key successfully generated.")
        public_key = generate_public_key(private_key)
        logger.debug(f"{DEBUG_EMOJI} Public key successfully generated.")
        preshared_key = generate_preshared_key()
        logger.debug(f"{DEBUG_EMOJI} Preshared key successfully generated.")

        # Calculate subnet
        subnet = calculate_subnet(params.get('SERVER_WG_IPV4', '10.66.66.1'))
        logger.debug(f"{DEBUG_EMOJI} Subnet being used: {subnet}")

        # Generate IP address
        new_ipv4 = generate_next_ip(config_file, subnet)
        logger.info(f"{INFO_EMOJI} New user IP address: {new_ipv4}")

        # Generate client configuration
        client_config = create_client_config(
            private_key=private_key,
            address=new_ipv4,
            dns_servers=dns_servers,
            server_public_key=server_public_key,
            preshared_key=preshared_key,
            endpoint=endpoint
        )
        logger.debug(f"{DEBUG_EMOJI} Client configuration successfully created.")

        config_path = os.path.join(settings.WG_CONFIG_DIR, f"{nickname}.conf")
        qr_path = os.path.join(settings.QR_CODE_DIR, f"{nickname}.png")

        # Save configuration
        os.makedirs(settings.WG_CONFIG_DIR, exist_ok=True)
        with open(config_path, "w") as file:
            file.write(client_config)
        logger.info(f"{INFO_EMOJI} User configuration saved to {config_path}")

        # Generate QR code
        generate_qr_code(client_config, qr_path)

        # Add user to server configuration
        add_user_to_server_config(config_file, nickname, public_key.decode('utf-8'), preshared_key.decode('utf-8'), new_ipv4)
        logger.info(f"{INFO_EMOJI} User successfully added to the server configuration.")

        # Add user record
        user_record = create_user_record(
            username=nickname,
            address=new_ipv4,
            public_key=public_key.decode('utf-8'),
            preshared_key=preshared_key.decode('utf-8'),
            qr_code_path=qr_path,
            email=email,
            telegram_id=telegram_id
        )
        logger.debug(f"{DEBUG_EMOJI} User record created.")

        # Save to database
        user_records_path = os.path.join("user", "data", "user_records.json")
        os.makedirs(os.path.dirname(user_records_path), exist_ok=True)
        with open(user_records_path, "r+", encoding="utf-8") as file:
            try:
                user_data = json.load(file)
                logger.debug(f"{DEBUG_EMOJI} Loaded existing user records.")
            except json.JSONDecodeError:
                user_data = {}
                logger.warning(f"{WARNING_EMOJI} Error reading user database, a new one will be created.")
            user_data[nickname] = user_record
            file.seek(0)
            json.dump(user_data, file, indent=4)
            file.truncate()
        logger.info(f"{INFO_EMOJI} User data for {nickname} successfully added to {user_records_path}")

        # Sync WireGuard
        params_path = "/etc/wireguard/params"
        if os.path.exists(params_path):
            with open(params_path, "r") as file:
                for line in file:
                    if line.startswith("SERVER_WG_NIC="):
                        server_wg_nic = line.strip().split("=")[1].strip('"')
                        break
                else:
                    raise ValueError("SERVER_WG_NIC not found in /etc/wireguard/params.")
        else:
            raise FileNotFoundError(f"File {params_path} not found.")

        sync_command = f'wg syncconf "{server_wg_nic}" <(wg-quick strip "{server_wg_nic}")'
        subprocess.run(sync_command, shell=True, check=True, executable='/bin/bash')
        logger.info(f"WireGuard synchronized for interface {server_wg_nic}")

        logger.info("+--------- Process 🌱 User Creation Completed --------------+\n")
        return config_path, qr_path
    except Exception as e:
        logger.error(f"Execution error: {e}")
        logger.info("+--------- Process 🌱 User Creation Completed --------------+\n")
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Not enough arguments. Usage: python3 main.py <nickname> [email] [telegram_id]")
        sys.exit(1)

    nickname = sys.argv[1]
    email = sys.argv[2] if len(sys.argv) > 2 else "N/A"
    telegram_id = sys.argv[3] if len(sys.argv) > 3 else "N/A"
    params_file = settings.PARAMS_FILE

    logger.info("Starting the WireGuard user creation process.")
    try:
        logger.info("Initializing directories.")
        setup_directories()

        logger.info(f"Loading parameters from file: {params_file}")
        params = load_params(params_file)

        logger.info("Checking for existing user.")
        existing_users = load_existing_users()
        if nickname.lower() in existing_users:
            logger.error(f"User with name '{nickname}' already exists in the database.")
            sys.exit(1)

        if is_user_in_server_config(nickname, settings.SERVER_CONFIG_FILE):
            logger.error(f"User with name '{nickname}' already exists in the server configuration.")
            sys.exit(1)

        logger.info("Generating user configuration.")
        config_file = settings.SERVER_CONFIG_FILE
        config_path, qr_path = generate_config(nickname, params, config_file, email, telegram_id)

        logger.info(f"✅ User configuration saved to {config_path}")
        logger.info(f"✅ User QR code successfully saved to {qr_path}")
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except KeyError as e:
        logger.error(f"Missing key in parameters: {e}")
    except ValueError as e:
        logger.error(f"Parameter value error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
