#!/usr/bin/env python3
# ai_diagnostics/ai_diagnostics_summary.py
# Script to generate a summary report on the state of the pyWGgen project.
# Version: 1.7
# Updated: 2024-12-02

import json
import subprocess
from pathlib import Path
import sys
import logging
import time

# Add the project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))  # Add the project root to sys.path

# Import settings
from settings import PROJECT_DIR, SUMMARY_REPORT_PATH, USER_DB_PATH, LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=logging.getLevelName(LOG_LEVEL),  # Use log level from settings
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("diagnostics_summary.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def run_command(command):
    """Executes a terminal command and returns the result."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command {command}: {e.stderr.strip()}")
        return f"Error: {e.stderr.strip()}"


def check_ports():
    """Checks open ports."""
    command = ["ss", "-tuln"]
    result = run_command(command)
    open_ports = []
    if not result:
        logger.warning("Failed to retrieve the list of open ports.")
        return open_ports

    for line in result.splitlines():
        if ":51820" in line:
            open_ports.append("51820 (WireGuard)")
        if ":7860" in line:
            open_ports.append("7860 (Gradio)")
    logger.debug(f"Open ports: {open_ports}")
    return open_ports


def check_firewall():
    """Checks the status of the firewall and open ports."""
    command_status = ["firewall-cmd", "--state"]
    command_ports = ["firewall-cmd", "--list-ports"]
    status = run_command(command_status)
    if status != "running":
        logger.warning(f"Firewall inactive: {status}")
        return f"Firewall: {status}", []
    open_ports = run_command(command_ports).split()
    logger.debug(f"Open firewall ports: {open_ports}")
    return f"Firewall: Active", open_ports


def check_wireguard_status():
    """Checks if the WireGuard service is active."""
    command_status = ["sudo", "systemctl", "is-active", "wg-quick@wg0"]
    command_info = ["sudo", "wg", "show"]
    status = run_command(command_status)
    logger.debug(f"WireGuard status: {status}")

    if status == "active":
        wg_info = run_command(command_info)
        logger.debug(f"WireGuard info:\n{wg_info}")
        return status, wg_info
    return status, "WireGuard inactive"


def count_users():
    """Counts the number of users from user_records.json."""
    if USER_DB_PATH.exists():
        try:
            with open(USER_DB_PATH, "r", encoding="utf-8") as file:
                user_data = json.load(file)
                user_count = len(user_data)
                logger.debug(f"Detected users: {user_count}")
                return user_count, "user_records.json"
        except json.JSONDecodeError:
            logger.error("Error reading user_records.json.")
            return 0, "Error reading user_records.json"
    logger.warning("File user_records.json is missing.")
    return 0, "Missing file user_records.json"


def count_peers(wg_info):
    """Counts the number of peers from wg show output."""
    if not wg_info:
        logger.warning("WireGuard information unavailable.")
        return 0
    peer_count = sum(1 for line in wg_info.splitlines() if line.startswith("peer:"))
    logger.debug(f"Number of peers: {peer_count}")
    return peer_count


def generate_summary():
    """Generates a summary report on the state of the pyWGgen project."""
    logger.info("Starting summary report generation.")

    # Retrieve user data
    total_users, user_source = count_users()

    # Check WireGuard status
    wg_status, wg_info = check_wireguard_status()
    peers_count = count_peers(wg_info) if wg_status == "active" else 0

    # Check ports
    open_ports = check_ports()

    # Check firewall status
    firewall_status, firewall_ports = check_firewall()

    # Create report
    summary = [
        " 📂 Users:",
        f"- Total users: {total_users} (Source: {user_source})",
        "\n 🔒 WireGuard:",
        f" - Total peers: {peers_count} (Source: wg show)",
        f" - WireGuard status: {wg_status}",
        f" - WireGuard info:\n{wg_info if wg_status == 'active' else ''}",
        "\n 🌐 Gradio:",
        f" - Status: {'Not running' if '7860 (Gradio)' not in open_ports else 'Running'}",
        "   - To start:",
        f"    1️⃣  Navigate to the project root:",
        "    2️⃣  Execute \"🌐 Open Gradio Admin\"",
        "\n 🔥 Firewall:",
        f" - {firewall_status}",
        " - Open ports:",
        f"  - {', '.join(firewall_ports) if firewall_ports else 'No open ports'}",
        "\n 🎯 Recommendations:",
        " - Ensure the number of peers matches the number of users.",
        " - If Gradio is not running, follow the suggested steps.",
        " - Verify that ports for Gradio and WireGuard are accessible through the firewall.\n\n"
    ]

    # Save report
    try:
        with open(SUMMARY_REPORT_PATH, "w", encoding="utf-8") as file:
            file.write("\n".join(summary))
        logger.info(f"Summary report saved: {SUMMARY_REPORT_PATH}")
        print(f"\n ✅ Summary report saved:\n 📂 {SUMMARY_REPORT_PATH}")
        time.sleep(2.5)
    except IOError as e:
        logger.error(f"Error saving summary report: {e}\n")
        print(f" ❌ Error saving report: {e}\n")


if __name__ == "__main__":
    generate_summary()
