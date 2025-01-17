#!/usr/bin/env python3
# modules/install_wg.py
# ===========================================
# WireGuard Installer with Full Parameter Support
# Version 2.8
# ===========================================
# Purpose:
# - Install and configure WireGuard on CentOS 8 / CentOS Stream 8.
# - Generate the wg0.conf configuration file.
# - Create parameters in the /etc/wireguard/params file.
# - Save user parameters in the .env file.
# - Configure firewalld for WireGuard.
#
# Features:
# - Support for interactive input of subnet and port.
# - Full compatibility with bash script functionality.
# ===========================================

import os
import subprocess
import shutil
from pathlib import Path
import ipaddress
from modules.firewall_utils import get_external_ip
from settings import DEFAULT_SUBNET, WIREGUARD_PORT, SERVER_CONFIG_FILE, PARAMS_FILE

ENV_FILE = Path(".env")

def log_message(message: str, level: str = "INFO"):
    """Logs a message."""
    print(f"{level}: {message}")

def is_root():
    """Checks if the script is run as root."""
    if os.geteuid() != 0:
        raise PermissionError("The script must be run as root.")

def check_os():
    """Checks that the OS is CentOS 8 or CentOS Stream 8."""
    with open("/etc/os-release") as f:
        os_info = f.read()
    if not (("CentOS" in os_info and "8" in os_info) or "CentOS Stream 8" in os_info):
        raise EnvironmentError("CentOS Linux 8 or CentOS Stream 8 is required.")

def create_wireguard_directory():
    """Creates the /etc/wireguard directory if it does not exist."""
    wg_dir = Path("/etc/wireguard")
    if not wg_dir.exists():
        wg_dir.mkdir(mode=0o700, parents=True)
        log_message("Created directory /etc/wireguard")

def detect_server_ip_and_nic():
    """Detects the server's public IP address and network interface."""
    try:
        server_pub_nic = subprocess.check_output(
            ["ip", "route", "show", "default"], text=True
        ).split()[4]

        server_pub_ip = get_external_ip()

        if not server_pub_ip or server_pub_ip.startswith("N/A"):
            raise RuntimeError("Failed to determine external IP address.")
        return server_pub_ip, server_pub_nic
    except (IndexError, subprocess.CalledProcessError) as e:
        raise RuntimeError(f"Error determining IP address or network interface: {e}")

def write_env_file(subnet, port):
    """Creates a .env file with user parameters."""
    dns = "1.1.1.1, 1.0.0.1, 8.8.8.8"
    env_content = f"""
# WireGuard Parameters (set by user)
WIREGUARD_PORT={port}
DEFAULT_SUBNET="{DEFAULT_SUBNET}"
USER_SET_SUBNET="{subnet}"
DNS_WIREGUARD="{dns}"
"""
    with open(ENV_FILE, "w") as env_file:
        env_file.write(env_content.strip() + "\n")  # Ensure newline at the end
    log_message(f".env file created: {ENV_FILE}")

def write_params_file(subnet, port, private_key, public_key):
    """Creates the /etc/wireguard/params file with server parameters."""
    server_pub_ip, server_pub_nic = detect_server_ip_and_nic()

    # Ensure SERVER_WG_IPV4 uses the first IP from the subnet
    server_wg_ipv4 = str(ipaddress.ip_network(subnet, strict=False).network_address + 1)

    params_content = f"""
[server]
SERVER_PUB_IP={server_pub_ip}
SERVER_PUB_NIC={server_pub_nic}
SERVER_WG_NIC=wg0
SERVER_WG_IPV4={server_wg_ipv4}
SERVER_WG_IPV6=fd42:42:42::1
SERVER_PORT={port}
SERVER_PRIV_KEY={private_key}
SERVER_PUB_KEY={public_key}
CLIENT_DNS_1=1.1.1.1
CLIENT_DNS_2=1.0.0.1
"""
    with open(PARAMS_FILE, "w") as params_file:
        params_file.write(params_content.strip() + "\n")  # Ensure newline at the end
    os.chmod(PARAMS_FILE, 0o600)
    log_message(f"Parameters file created: {PARAMS_FILE}")

def validate_subnet(subnet):
    """Validates the subnet."""
    try:
        ipaddress.ip_network(subnet, strict=True)
        return subnet
    except ValueError:
        raise ValueError(f"Invalid subnet: {subnet}")

def prompt_parameters():
    """Prompts the user for WireGuard parameters."""
    subnet = input(f"Enter WireGuard subnet [{DEFAULT_SUBNET}]: ") or DEFAULT_SUBNET
    subnet = validate_subnet(subnet)

    port = input(f"Enter WireGuard port [{WIREGUARD_PORT}]: ") or WIREGUARD_PORT
    port = int(port)

    return subnet, port

def generate_keypair():
    """Generates private and public keys."""
    wg_path = shutil.which("wg")
    if not wg_path:
        raise RuntimeError("WireGuard is not installed. Install it before proceeding.")
    private_key = subprocess.check_output([wg_path, "genkey"]).decode().strip()
    public_key = subprocess.check_output([wg_path, "pubkey"], input=private_key.encode()).decode().strip()
    return private_key, public_key

def generate_wg_config(subnet, port):
    """Generates the WireGuard configuration."""
    base_subnet = subnet.split("/")[0]
    server_private_key, server_public_key = generate_keypair()

    server_pub_ip, server_pub_nic = detect_server_ip_and_nic()

    server_config = f"""
[Interface]
Address = {subnet},fd42:42:42::1/64
ListenPort = {port}
PrivateKey = {server_private_key}
PostUp = firewall-cmd --add-port {port}/udp && firewall-cmd --add-rich-rule='rule family=ipv4 source address={base_subnet}/24 masquerade' && firewall-cmd --add-rich-rule='rule family=ipv6 source address=fd42:42:42::0/64 masquerade'
PostDown = firewall-cmd --remove-port {port}/udp && firewall-cmd --remove-rich-rule='rule family=ipv4 source address={base_subnet}/24 masquerade' && firewall-cmd --remove-rich-rule='rule family=ipv6 source address=fd42:42:42::0/64 masquerade'
    """
    with open(SERVER_CONFIG_FILE, "w") as config_file:
        config_file.write(server_config)

    write_params_file(subnet, port, server_private_key, server_public_key)
    write_env_file(subnet, port)
    return server_private_key, server_public_key

def configure_firewalld(port, subnet):
    """Configures firewalld."""
    base_subnet = subnet.split("/")[0]
    subprocess.run(["firewall-cmd", "--add-port", f"{port}/udp", "--permanent"], check=True)
    subprocess.run(["firewall-cmd", "--add-rich-rule", f"rule family=ipv4 source address={base_subnet}/24 masquerade", "--permanent"], check=True)
    subprocess.run(["firewall-cmd", "--add-rich-rule", "rule family=ipv6 source address=fd42:42:42::0/64 masquerade", "--permanent"], check=True)
    subprocess.run(["firewall-cmd", "--reload"], check=True)

def enable_and_start_service(port):
    """Enables and starts WireGuard."""
    service_name = f"wg-quick@wg0"
    subprocess.run(["systemctl", "enable", service_name], check=True)
    subprocess.run(["systemctl", "start", service_name], check=True)
    log_message(f"WireGuard successfully started on port {port}.")

def install_wireguard_packages():
    """Installs all necessary packages for WireGuard."""
    log_message("Installing packages for WireGuard...")
    try:
        subprocess.run(["dnf", "install", "-y", "epel-release", "elrepo-release"], check=True)
        subprocess.run(["dnf", "install", "-y", "wireguard-tools", "kmod-wireguard", "qrencode", "iptables"], check=True)
        log_message("All packages installed successfully.")
    except subprocess.CalledProcessError as e:
        log_message(f"Error installing packages: {e}", level="ERROR")
        raise

def install_wireguard():
    """Installs WireGuard with configuration."""
    try:
        is_root()
        check_os()
        create_wireguard_directory()

        subnet, port = prompt_parameters()

        install_wireguard_packages()

        generate_wg_config(subnet, port)
        configure_firewalld(port, subnet)
        enable_and_start_service(port)

        log_message("✅ WireGuard installation completed.")
    except Exception as e:
        log_message(f"Error: {e}", level="ERROR")

if __name__ == "__main__":
    install_wireguard()
