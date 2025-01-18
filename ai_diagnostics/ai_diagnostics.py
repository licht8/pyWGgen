#!/usr/bin/env python3
# ai_diagnostics/ai_diagnostics.py
# Script for diagnosing and analyzing the state of the pyWGgen project.
# Version: 5.3
# Updated: 2024-12-02 22:00

import json
import time
import sys
import subprocess
import logging
from pathlib import Path

# Define project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = PROJECT_ROOT / "modules"
DIAGNOSTICS_DIR = PROJECT_ROOT / "ai_diagnostics"
SETTINGS_PATH = PROJECT_ROOT / "settings.py"

# Add paths to sys.path
sys.path.extend([str(PROJECT_ROOT), str(MODULES_DIR)])

# Check if settings.py exists
if not SETTINGS_PATH.exists():
    raise FileNotFoundError(f"Settings file settings.py not found at: {SETTINGS_PATH}")

# Import settings
from settings import (
    DEBUG_REPORT_PATH,
    TEST_REPORT_PATH,
    MESSAGES_DB_PATH,
    PROJECT_DIR,
    LOG_LEVEL,
    LOG_FILE_PATH,
    ANIMATION_SPEED,
    PRINT_SPEED,
    LINE_DELAY,
    GRADIO_PORT,
    USER_DB_PATH,
    QR_CODE_DIR,
    WIREGUARD_PORT,
)

# Import WireGuard subnet function
from utils import get_wireguard_subnet

# Configure logging
LOG_DIR = Path(LOG_FILE_PATH).parent
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.getLevelName(LOG_LEVEL),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Ports to check
REQUIRED_PORTS = [f"{WIREGUARD_PORT}/udp", f"{GRADIO_PORT}/tcp"]

# Scripts
SUMMARY_SCRIPT = DIAGNOSTICS_DIR / "ai_diagnostics_summary.py"

def check_gradio_status():
    """Checks if Gradio is running on the specified port."""
    command = ["ss", "-tuln"]
    result = run_command(command)
    if not result:
        return False

    logger.debug(f"Gradio status check result:\n{result}")

    for line in result.splitlines():
        if f":{GRADIO_PORT} " in line and "LISTEN" in line:
            return True
    return False

def execute_commands(commands):
    """Executes a list of commands and returns the results."""
    results = []
    for command in commands:
        logger.info(f"Executing command: {command}")
        try:
            result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            results.append(f"{command}:\n{result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            results.append(f"{command}:\nError: {e.stderr.strip()}")
    return "\n".join(results)


def run_command(command):
    """Runs an external command and returns its output."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command {' '.join(command)}: {e.stderr.strip()}")
        return None


def check_ports():
    """Checks the status of required ports."""
    command = ["sudo", "firewall-cmd", "--list-all"]
    result = run_command(command)
    if not result:
        return []

    logger.debug(f"Port check result:\n{result}")
    open_ports = []
    for line in result.splitlines():
        if "ports:" in line:
            ports_line = line.split("ports:")[1].strip()
            open_ports.extend(ports_line.split())
    return [port for port in REQUIRED_PORTS if port not in open_ports]


def check_masquerade_rules():
    """Checks masquerade rules for WireGuard."""
    command = ["sudo", "firewall-cmd", "--list-all"]
    result = run_command(command)
    if not result:
        return [{"type": "Error", "rule": "Failed to check masquerade rules"}]

    logger.debug(f"Masquerade check result:\n{result}")
    try:
        wireguard_subnet = get_wireguard_subnet()
        required_rules = [
            {"type": "IPv4", "rule": f"{wireguard_subnet.split('/')[0].rsplit('.', 1)[0]}.0/24"},
            {"type": "IPv6", "rule": "fd42:42:42::0/24"}
        ]
    except Exception as e:
        logger.error(f"Error extracting WireGuard subnet: {e}")
        return [{"type": "Error", "rule": "Failed to determine rules"}]

    missing_rules = []
    for rule in required_rules:
        rule_str = f'rule family="{rule["type"].lower()}" source address="{rule["rule"]}" masquerade'
        if rule_str not in result:
            missing_rules.append(rule)

    return missing_rules


def parse_reports(messages_db_path):
    """Parses reports for analysis."""
    try:
        with open(messages_db_path, "r", encoding="utf-8") as db_file:
            messages_db = json.load(db_file)
    except FileNotFoundError:
        logger.error(f" ❌ messages_db.json file not found: {messages_db_path}")
        return [], []

    findings, suggestions = [], []

    # Check closed ports
    closed_ports = check_ports()
    if closed_ports:
        report = messages_db.get("ports_closed", {})
        if report:
            report["message"] = report["message"].format(
                PROJECT_DIR=PROJECT_DIR,
                USER_DB_PATH=USER_DB_PATH,
                QR_CODE_DIR=QR_CODE_DIR
            )
            findings.append(report)

    # Check masquerade status
    missing_masquerade_rules = check_masquerade_rules()
    if missing_masquerade_rules:
        max_key_length = max(len(rule['type']) for rule in missing_masquerade_rules if isinstance(rule, dict))
        formatted_rules = "\n".join(
            f"        {rule['type']:<{max_key_length}}: {rule['rule']}" if isinstance(rule, dict) else f"        {rule}"
            for rule in missing_masquerade_rules
        )
        report = messages_db.get("masquerade_issue", {})
        if report:
            report["message"] = report["message"].format(
                MISSING_RULES=formatted_rules
            )
            findings.append(report)

    # Check Gradio status
    if not check_gradio_status():
        report = messages_db.get("gradio_not_running", {})
        if report:
            report["message"] = report["message"].format(
                PROJECT_DIR=PROJECT_DIR,
                GRADIO_PORT=GRADIO_PORT
            )
            suggestions.append(report)

    return findings, suggestions


def display_message_slowly(message, print_speed=None, end="\n", indent=True):
    """
    Prints a message line by line with optional indentation and custom speed.

    :param message: Message to display.
    :param print_speed: Character printing speed (in seconds). If None, global PRINT_SPEED is used.
    :param end: End character for the line (default: "\\n").
    :param indent: If True, adds a 3-space indent before each line.
    """
    effective_speed = print_speed if print_speed is not None else PRINT_SPEED
    for line in message.split("\n"):
        if indent:
            print("   ", end="")  # Add indent if indent=True
        for char in line:
            print(char, end="", flush=True)
            time.sleep(effective_speed)
        print(end, end="", flush=True)
        time.sleep(LINE_DELAY)


def handle_findings(findings):
    """Handles detected issues."""
    for finding in findings:
        display_message_slowly(f"\n {finding['title']}\n{finding['message']}")
        
        commands = finding.get("commands", [])
        if commands:
            response = input(f"    🛠  Fix automatically? (y/n): ").strip().lower()
            if response in ["y", "yes"]:
                display_message_slowly(f" ⚙️  Fixing...\n")
                result = execute_commands(commands)
                display_message_slowly(f" 📝 Result:\n    {result}")
            elif response in ["n", "no"]:
                display_message_slowly(f" 🚫 Skipping fix.\n")
            else:
                display_message_slowly(f" ⚠️ Invalid input. Skipping fix.\n")


def main():
    """Main program execution."""
    logger.info("Starting diagnostics")
    display_message_slowly("\n 🎯  Here's what we found:")

    findings, suggestions = parse_reports(MESSAGES_DB_PATH)

    if findings:
        handle_findings(findings)

    if suggestions:
        for suggestion in suggestions:
            display_message_slowly(f"\n {suggestion['title']}\n {suggestion['message']}")

    if not findings and not suggestions:
        display_message_slowly(f" ✅  Everything is fine!\n 👍  No issues detected.\n")

    subprocess.run([sys.executable, str(SUMMARY_SCRIPT)])


if __name__ == "__main__":
    main()
