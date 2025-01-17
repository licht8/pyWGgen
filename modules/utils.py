#!/usr/bin/env python3
# utils.py
# Utility functions for the wg_qr_generator project.

import json
import os
import datetime

def read_json(file_path):
    """
    Read data from a JSON file.
    :param file_path: Path to the JSON file.
    :return: File content as a dictionary.
    """
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json(file_path, data):
    """
    Write data to a JSON file.
    :param file_path: Path to the JSON file.
    :param data: Data to write.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def get_wireguard_config_path():
    """
    Get the path to the current WireGuard configuration file.
    :return: Path to the configuration file.
    """
    return "/etc/wireguard/wg0.conf"

def parse_wireguard_config(config_path=None):
    """
    Read and parse the WireGuard configuration file.
    :param config_path: Path to the configuration file.
    :return: File content as a string.
    """
    if config_path is None:
        config_path = get_wireguard_config_path()

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"WireGuard configuration file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as file:
        return file.read()

def get_wireguard_subnet(config_path=None):
    """
    Extract the WireGuard subnet from the configuration file.
    :param config_path: Path to the configuration file.
    :return: Subnet as a string (e.g., "10.66.66.1/24").
    """
    if config_path is None:
        config_path = get_wireguard_config_path()

    config_content = parse_wireguard_config(config_path)
    for line in config_content.splitlines():
        if line.strip().startswith("Address"):
            addresses = line.split('=')[1].strip().split(',')
            for address in addresses:
                if '/' in address and '.' in address:  # IPv4
                    return address.strip()
    raise ValueError(f"Failed to find the WireGuard subnet in the configuration file {config_path}.")

def log_debug(message):
    """
    Log debug messages.
    :param message: Message to log.
    """
    timestamp = datetime.datetime.now().isoformat()
    log_file_path = "debug.log"
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"[DEBUG] {timestamp} - {message}\n")
    print(f"[DEBUG] {timestamp} - {message}")
