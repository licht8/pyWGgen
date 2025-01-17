#!/usr/bin/env python3
# ai_assistant/scripts/wg_data_analyzer.py
# ==================================================
# Script for collecting and analyzing WireGuard data.
# Version: 2.5 (2024-12-21)
# ==================================================
# Description:
# This script collects data from three sources:
# - The `sudo wg show` command (current WireGuard status);
# - The configuration file `/etc/wireguard/wg0.conf`;
# - The parameters file `/etc/wireguard/params`.
#
# The data is analyzed and saved in JSON format for further
# use, including sending to an LLM for processing.
#
# The script can function either as a module (calling functions)
# or as a standalone file.
# ==================================================

import subprocess
import json
import os
import sys
import requests
from pathlib import Path
import logging
import uuid

# Ensure the path to settings.py is accessible
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:
    SCRIPT_DIR = Path.cwd()

PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Attempt to import project settings
try:
    from settings import BASE_DIR, SERVER_CONFIG_FILE, PARAMS_FILE, LLM_API_URL
except ModuleNotFoundError as e:
    logger = logging.getLogger(__name__)
    logger.error("Unable to find the settings module. Ensure settings.py is located in the project root.")
    print("Unable to find the settings module. Ensure settings.py is located in the project root.")
    sys.exit(1)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler(BASE_DIR / "ai_assistant/logs/llm_interaction.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def get_last_restart():
    """Gets the last restart time of WireGuard."""
    try:
        output = subprocess.check_output(["systemctl", "show", "wg-quick@wg0", "--property=ActiveEnterTimestamp"], text=True)
        if "ActiveEnterTimestamp=" in output:
            return output.split("ActiveEnterTimestamp=")[1].strip()
        else:
            return "No data"
    except Exception as e:
        logger.error(f"Error retrieving WireGuard restart time: {e}")
        return "No data"

def get_wg_status():
    """Gets the WireGuard status using the `wg show` command."""
    try:
        output = subprocess.check_output(["sudo", "wg", "show"], text=True)
        return output
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing wg show command: {e}")
        return f"Error executing wg show: {e}"

def read_config_file(filepath):
    """Reads the contents of a configuration file."""
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return f"File not found: {filepath}"
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return f"Error reading file {filepath}: {e}"

def parse_wg_show(output):
    """Parses the output of the `wg show` command and extracts peer data."""
    def convert_to_simple_format(size_str):
        """Converts size strings to a simple format (MB or GB)."""
        try:
            size, unit = size_str.split()
            size = float(size)
            if unit.lower().startswith("kib"):
                size_mb = size / 1024
                return f"{size_mb:.2f} MB"
            elif unit.lower().startswith("mib"):
                return f"{size:.2f} MB"
            elif unit.lower().startswith("gib"):
                return f"{size:.2f} GB"
            else:
                return size_str
        except Exception:
            return "No data"

    peers = []
    current_peer = None

    for line in output.splitlines():
        line = line.strip()
        if line.startswith("peer:"):
            if current_peer:
                peers.append(current_peer)
            current_peer = {
                "PublicKey": line.split("peer:")[1].strip(),
                "Transfer": {"Received": "No data", "Sent": "No data"},
                "LatestHandshake": "No data"
            }
        elif "latest handshake:" in line and current_peer:
            handshake_data = line.split("latest handshake:")[1].strip()
            current_peer["LatestHandshake"] = handshake_data if handshake_data else "No data"
        elif "transfer:" in line and current_peer:
            transfer_data = line.split("transfer:")[1].split(",")
            if len(transfer_data) == 2:
                current_peer["Transfer"] = {
                    "Received": convert_to_simple_format(transfer_data[0].strip()) or "No data",
                    "Sent": convert_to_simple_format(transfer_data[1].strip()) or "No data"
                }

    if current_peer:
        peers.append(current_peer)

    return {"peers": peers}

def parse_config_with_logins(content):
    """Parses the WireGuard configuration file and matches peers with logins."""
    peer_data = []
    current_login = None
    current_peer = {}

    for line in content.splitlines():
        line = line.strip()
        if line.startswith("### Client"):
            if current_peer:
                peer_data.append(current_peer)
            current_login = line.split("Client")[-1].strip()
            current_peer = {"login": current_login, "peer": {}}
        elif line.startswith("[Peer]"):
            if current_peer:
                peer_data.append(current_peer)
            current_peer = {"login": current_login, "peer": {}}
        elif "=" in line:
            key, value = map(str.strip, line.split("=", 1))
            if current_peer:
                current_peer["peer"][key] = value

    if current_peer:
        peer_data.append(current_peer)

    return peer_data

def parse_config_file(content):
    """Parses the contents of a configuration file and returns a dictionary."""
    config = {}
    for line in content.splitlines():
        if "=" in line:
            key, value = map(str.strip, line.split("=", 1))
            config[key] = value
    return config

def collect_and_analyze_wg_data():
    """Collects data from sources and returns it as a dictionary."""
    data = {}

    # Data collection
    wg_status = get_wg_status()
    wg0_config = read_config_file(SERVER_CONFIG_FILE)
    params_config = read_config_file(PARAMS_FILE)

    # Data analysis
    data["wg_status"] = parse_wg_show(wg_status) if "Error" not in wg_status else wg_status
    data["wg0_config"] = parse_config_with_logins(wg0_config) if "Error" not in wg0_config else wg0_config
    data["params_config"] = parse_config_file(params_config) if "Error" not in params_config else params_config
    data["last_restart"] = get_last_restart()

    return data

def save_to_json(data, output_file):
    """Saves data in JSON format to the specified file."""
    try:
        with open(output_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        logger.info(f"Data saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving data to JSON: {e}")

def load_system_prompt(prompt_file):
    """Loads the system prompt from a file."""
    try:
        with open(prompt_file, 'r') as file:
            prompt_data = json.load(file)
        return prompt_data.get("system_prompt", "")
    except Exception as e:
        logger.error(f"Error loading system prompt: {e}")
        return ""

def query_llm(prompt, api_url=LLM_API_URL, model="llama3:latest", max_tokens=500):
    """Sends a query to the LLM and returns the response."""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "Error: no response")
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error when querying LLM: {http_err}")
        return f"HTTP Error: {http_err}"
    except Exception as e:
        logger.error(f"Error querying LLM: {e}")
        return f"Error: {e}"

def generate_prompt(system_prompt, wg_data):
    """Generates a final prompt for data analysis without duplication."""
    report_id = str(uuid.uuid4())
    formatted_prompt = (
        f"{system_prompt}\n\n"
        f"Unique report ID: {report_id}\n\n"
        f"**WireGuard Status:**\n"
    )

    for peer in wg_data['wg0_config']:
        formatted_prompt += (
            f"- Login: {peer['login']}, PublicKey: {peer['peer'].get('PublicKey', 'Not found')}\n"
        )

    formatted_prompt += (
        f"\n**Configuration:**\n"
        f"📊 Address: {wg_data['params_config'].get('SERVER_WG_IPV4', 'Not specified')}\n"
        f"📊 Port: {wg_data['params_config'].get('SERVER_PORT', 'Not specified')}\n"
        f"📊 PublicKey: {wg_data['params_config'].get('SERVER_PUB_KEY', 'Not specified')}\n"
    )

    formatted_prompt += (
        f"\n**Parameters:**\n"
        f"📊 Server IP: {wg_data['params_config'].get('SERVER_PUB_IP', 'Not specified')}\n"
        f"📊 DNS: {', '.join([wg_data['params_config'].get(f'CLIENT_DNS_{i}', '') for i in range(1, 5)])}\n"
    )

    formatted_prompt += (
        f"\n**Last Restart:**\n"
        f"🕒 {wg_data.get('last_restart', 'Not specified')}\n"
    )

    formatted_prompt += (
        f"\n**Recommendations:**\n"
        f"- 🔧 Check peer status: `wg show`\n"
        f"- 🔧 Restart WireGuard: `sudo systemctl restart wg-quick@wg0`\n"
        f"- 🔧 Check port availability: `sudo ss -tuln | grep 51820`\n"
    )

    return formatted_prompt

if __name__ == "__main__":
    output_path = BASE_DIR / "ai_assistant/inputs/wg_analysis.json"
    prompt_file = BASE_DIR / "ai_assistant/prompts/system_prompt.json"

    data = collect_and_analyze_wg_data()
    save_to_json(data, output_path)

    # Load the system prompt
    system_prompt = load_system_prompt(prompt_file)
    prompt = generate_prompt(system_prompt, data)

    # Query the LLM
    llm_response = query_llm(prompt)

    # Output the result
    print("\nLLM Analysis Output:")
    print(llm_response)
