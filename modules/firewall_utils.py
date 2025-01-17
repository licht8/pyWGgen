#!/usr/bin/env python3
# modules/firewall_utils.py
# Functions for managing ports via firewalld

import subprocess
import psutil
from modules.port_manager import handle_port_conflict

import socket


def get_external_ip():
    """
    Retrieves the external IP address through internal settings or network interfaces.

    :return: External IP address (string) or an error message.
    """
    try:
        # Attempt to determine the external IP via standard network interfaces
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to Google's public DNS server to determine the IP
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]  # Get the IP address from the socket
    except OSError as e:
        return f"N/A ❌ (Error: {e})"

def open_firewalld_port(port):
    """
    Opens a port in firewalld.

    :param port: The port number to open.
    """
    # Module for managing ports and resolving conflicts
    # Checks if the port is in use and prompts the user for actions.
    handle_port_conflict(port)
    print(f" 🔓  Opening port {port} via firewalld...\n")
    subprocess.run(["firewall-cmd", "--add-port", f"{port}/tcp"])
    # Uncomment the following line to reload firewalld after changes
    # subprocess.run(["firewall-cmd", "--reload"])

def close_firewalld_port(port):
    """
    Closes a port in firewalld.

    :param port: The port number to close.
    """
    print(f" 🔒  Closing port {port} via firewalld...\n")
    subprocess.run(["firewall-cmd", "--remove-port", f"{port}/tcp"])
    # Uncomment the following line to reload firewalld after changes
    # subprocess.run(["firewall-cmd", "--reload"])
