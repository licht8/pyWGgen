#!/usr/bin/env python3
# pyWGgen/settings.py
# ===========================================
# Settings for the pyWGgen project
# ===========================================
# This file contains the main settings for the project, including file paths,
# directories, configurations, and global parameters.
# It centralizes all important variables to simplify project maintenance.
#
# Example usage:
# ---------------------
# from settings import BASE_DIR, WG_CONFIG_DIR, GRADIO_PORT
# 
# print(f"Project base directory: {BASE_DIR}")
# print(f"WireGuard configuration directory: {WG_CONFIG_DIR}")
# print(f"Port for running Gradio: {GRADIO_PORT}")
#
# IMPORTANT: All paths and parameters should be specified relative to BASE_DIR.
# ===========================================
# Logging:
# The logging module is used to manage logging in the project.
# You can change the logging level through the LOG_LEVEL variable:
# - DEBUG: Displays all messages, including debug information.
# - INFO: Main actions without debug messages.
# - WARNING: Only warnings and errors.
# - ERROR: Only errors.
# Logs are written to both the console and a file specified in LOG_FILE_PATH.
#
# Version: 1.7 (2026-01-10) 6:39

from pathlib import Path
import os
import configparser

# Define the base path to the project root
BASE_DIR = Path(__file__).resolve().parent  # Path to the pyWGgen root directory
PROJECT_DIR = BASE_DIR  # For compatibility, PROJECT_DIR equals BASE_DIR

# File and directory paths
WG_CONFIG_DIR = BASE_DIR / "user/data/wg_configs"  # Path to user WireGuard configurations
QR_CODE_DIR = BASE_DIR / "user/data/qrcodes"      # Path to saved QR codes
STALE_CONFIG_DIR = BASE_DIR / "user/data/usr_stale_config"  # Path to stale user configurations
USER_DB_PATH = BASE_DIR / "user/data/user_records.json"  # User database
#IP_DB_PATH = BASE_DIR / "user/data/ip_records.json"      # IP address database
SERVER_CONFIG_FILE = Path("/etc/wireguard/wg0.conf")     # Path to WireGuard server configuration file
SERVER_BACKUP_CONFIG_FILE = Path("/etc/wireguard/wg0.conf.bak") # Path to WireGuard server backup configuration file
PARAMS_FILE = Path("/etc/wireguard/params")             # Path to WireGuard parameters file

# WireGuard parameters
DEFAULT_TRIAL_DAYS = 30  # Default account validity in days
WIREGUARD_PORT = 51820   # WireGuard server port (default) range [1-65535]
DEFAULT_SUBNET = "10.66.66.0/24"
USER_SET_SUBNET = DEFAULT_SUBNET
DNS_WIREGUAED = "1.1.1.1, 1.0.0.1, 8.8.8.8"

# Ollama
OLLAMA_HOST = "http://10.99.0.2:11434"
MODEL_NAME = "qwen2.5:3b"

# Логи
AI_ASSISTANT_LOG_DIR = "ai_assistant/logs"

# WireGuard
IGNORE_INTERFACES = ["wg-mgmt"]
WG_PORT = "51820/udp"

# Firewalld
FIREWALLD_ZONES = ["public", "internal", "external", "home", "trusted", "work", "dmz", "wg"]

# AI
AI_TEMPERATURE = 0.1
AI_TIMEOUT = 120
CHAT_TEMPERATURE = 0.2
CHAT_TIMEOUT = 90

# Logging settings
LOG_DIR = BASE_DIR / "user/data/logs"  # Directory for storing logs
DIAGNOSTICS_LOG = LOG_DIR / "diagnostics.log"  # Diagnostics log file
SUMMARY_REPORT_PATH = LOG_DIR / "summary_report.txt"  # File for storing summary reports
LOG_FILE_PATH = LOG_DIR / "app.log"  # Application log file
LOG_LEVEL = "DEBUG"  # Logging level: DEBUG, INFO, WARNING, ERROR

# Paths for reports and message database
DEBUG_REPORT_PATH = BASE_DIR / "ai_diagnostics/debug_report.txt"  # Path to diagnostics report
TEST_REPORT_PATH = BASE_DIR / "ai_diagnostics/test_report.txt"    # Path to test report
MESSAGES_DB_PATH = BASE_DIR / "ai_diagnostics/messages_db.json"   # Path to diagnostics message database

# Paths for help
HELP_JSON_PATH = BASE_DIR / "ai_diagnostics/ai_help/ai_help.json"  # New path for the help system

# Additional paths for modules and utilities
MODULES_DIR = BASE_DIR / "modules"            # Directory containing modules
AI_DIAGNOSTICS_DIR = BASE_DIR / "ai_diagnostics"  # Directory with diagnostic files

# Port for Gradio
GRADIO_PORT = 7860  # Port for running the Gradio interface

# LLM_API_URL
LLM_API_URL = "http://10.67.67.2:11434/api/generate"

# Animation and print speed settings
ANIMATION_SPEED = 0.2  # Delay between animation iterations (in seconds)
# Examples:
# - 0.1: Accelerated animation, suitable for short messages.
# - 0.2 (default): Standard speed, smooth animation for comfortable perception.
# - 0.3: Slightly slower, even smoother effect.
# - 0.5: Slow animation, emphasizes importance or draws attention.

PRINT_SPEED = 0.02  # Speed of character output (in seconds)
# Examples:
# - 0.02 (default): Standard speed, mimics manual typing.
# - 0.01: Fast typing, almost instantaneous.
# - 0.05: Slow typing, creates a thoughtful text effect.

LINE_DELAY = 0.1  # Delay between lines (in seconds)
# Examples:
# - 0.1 (default): Smooth transition between lines.
# - 0.05: Fast transition between lines, reduces output time.
# - 0.2: Slow transition, draws attention to the new line.

# Function to read SERVER_WG_NIC from the params file
def get_server_wg_nic(params_file):
    """
    Extracts the SERVER_WG_NIC value from the params file.
    :param params_file: Path to the params file
    :return: SERVER_WG_NIC value
    """
    if not os.path.exists(params_file):
        raise FileNotFoundError(f"File {params_file} not found.")

    with open(params_file, "r") as f:
        for line in f:
            if line.startswith("SERVER_WG_NIC="):
                # Extract the value after "=" and strip spaces
                return line.split("=")[1].strip()
    raise ValueError("SERVER_WG_NIC not found in the params file.")

# Define SERVER_WG_NIC
try:
    SERVER_WG_NIC = get_server_wg_nic(PARAMS_FILE)
except (FileNotFoundError, ValueError) as e:
    SERVER_WG_NIC = None
    print(f"⚠️ Failed to load SERVER_WG_NIC: {e}")

def check_paths():
    """Checks the existence of files and directories."""
    paths = {
        "BASE_DIR": BASE_DIR,
        "PROJECT_DIR": PROJECT_DIR,
        "WG_CONFIG_DIR": WG_CONFIG_DIR,
        "QR_CODE_DIR": QR_CODE_DIR,
        "USER_DB_PATH": USER_DB_PATH,
        #"IP_DB_PATH": IP_DB_PATH,
        "SERVER_CONFIG_FILE": SERVER_CONFIG_FILE,
        "PARAMS_FILE": PARAMS_FILE,
        "LOG_DIR": LOG_DIR,
        "DIAGNOSTICS_LOG": DIAGNOSTICS_LOG,
        "SUMMARY_REPORT_PATH": SUMMARY_REPORT_PATH,
        "DEBUG_REPORT_PATH": DEBUG_REPORT_PATH,
        "TEST_REPORT_PATH": TEST_REPORT_PATH,
        "MESSAGES_DB_PATH": MESSAGES_DB_PATH,
        "HELP_JSON_PATH": HELP_JSON_PATH,
        "MODULES_DIR": MODULES_DIR,
        "AI_DIAGNOSTICS_DIR": AI_DIAGNOSTICS_DIR,
    }
    status = []
    for name, path in paths.items():
        exists = " ✅  Available" if path.exists() else " ❌  Missing"
        status.append(f"{name}: {exists} ({path})")
    return "\n".join(status)


if __name__ == "__main__":
    print(f"\n === 🛠️  pyWGgen Project Status ===\n")
    print(f"  Project base directory: {BASE_DIR}")
    print(f"  Gradio port: {GRADIO_PORT}")
    print(f"  WireGuard port: {WIREGUARD_PORT}\n")
    print(f" === 📂  Checking files and directories ===\n")
    print(check_paths())
    print(f"\n")
