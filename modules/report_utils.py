#!/usr/bin/env python3
# modules/report_utils.py
# ===========================================
# Module for handling reports in the pyWGgen project
# ===========================================
# This module provides functions for generating and displaying reports,
# including full reports, brief reports, summary reports, and project status information.
#
# Version: 2.1
# Updated: 2024-12-10

import os
import json
import subprocess
import platform
import psutil
import time
from datetime import datetime
from termcolor import colored
from pathlib import Path
from modules.firewall_utils import get_external_ip
from settings import SUMMARY_REPORT_PATH, TEST_REPORT_PATH
from modules.test_report_generator import generate_report

# Path to the script for creating summary_report
SUMMARY_SCRIPT = Path(__file__).resolve().parent.parent / "ai_diagnostics" / "ai_diagnostics_summary.py"

from datetime import datetime, timedelta

def create_summary_report():
    """Checks if the report is up-to-date and calls the script to create summary_report.txt if needed."""
    try:
        # Check if the file exists
        if SUMMARY_REPORT_PATH.exists():
            # Get the file's last modified time
            last_modified = datetime.fromtimestamp(SUMMARY_REPORT_PATH.stat().st_mtime)
            age = datetime.now() - last_modified

            if age < timedelta(minutes=1):
                print(f" ✅ File {SUMMARY_REPORT_PATH} is up-to-date. Recreation not required.")
                return
            else:
                print(f" ⏳ File {SUMMARY_REPORT_PATH} is outdated ({age.seconds // 60} minutes). Recreating...")

        else:
            print(f" ⏳ File {SUMMARY_REPORT_PATH} is missing. Creating...")

        # Explicit call via Python
        subprocess.run(["python3", str(SUMMARY_SCRIPT)], check=True)
        
        print(f" ✅ File {SUMMARY_REPORT_PATH} successfully created.")
    except subprocess.CalledProcessError as e:
        print(f" ❌ Error running script {SUMMARY_SCRIPT}: {e}")
    except Exception as e:
        print(f" ❌ Unexpected error while creating file {SUMMARY_REPORT_PATH}: {e}")

def get_open_ports():
    """Returns a list of open ports in firewalld."""
    try:
        output = subprocess.check_output(["sudo", "firewall-cmd", "--list-ports"], text=True)
        return output.strip() if output else colored("No open ports ❌", "red")
    except subprocess.CalledProcessError:
        return colored("Error retrieving data ❌", "red")

def get_wireguard_status():
    """Returns the status of WireGuard."""
    try:
        output = subprocess.check_output(["systemctl", "is-active", "wg-quick@wg0"], text=True).strip()
        if output == "active":
            return colored("active ✅", "green")
        return colored("inactive ❌", "red")
    except subprocess.CalledProcessError:
        return colored("not installed ❌", "red")

def get_wireguard_peers():
    """Gets a list of active WireGuard peers."""
    try:
        output = subprocess.check_output(["wg", "show"], text=True).splitlines()
        peers = [line.split(":")[1].strip() for line in output if line.startswith("peer:")]
        if peers:
            return f"{len(peers)} active peers ✅"
        return colored("No active peers ❌", "red")
    except FileNotFoundError:
        return colored("Command 'wg' not found ❌", "red")
    except subprocess.CalledProcessError:
        return colored("Error retrieving data ❌", "red")

def get_users_data():
    """Retrieves user information from user_records.json."""
    user_records_path = os.path.join("user", "data", "user_records.json")
    try:
        with open(user_records_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return colored("File user_records.json is missing ❌", "red")
    except json.JSONDecodeError:
        return colored("File user_records.json is corrupted ❌", "red")

def get_gradio_status(port=7860):
    """Checks the status of Gradio."""
    try:
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            cmdline = proc.info.get("cmdline", [])
            if cmdline and "gradio" in " ".join(cmdline) and str(port) in " ".join(cmdline):
                return f"running (PID {proc.info['pid']}) ✅"
        return colored("not running ❌", "red")
    except Exception as e:
        return colored(f"Error checking Gradio: {e} ❌", "red")

def get_gradio_port_status(port=7860):
    """Checks if the Gradio port is open."""
    open_ports = get_open_ports()
    if f"{port}/tcp" in open_ports:
        return colored("open ✅", "green")
    return colored("closed ❌", "red")

def show_project_status():
    """Displays the project status."""
    print("=== Project Status Summary ===\n")

    # System information
    print(f" 🖥️   OS: {platform.system()} {platform.release()}")
    print(f" 🧰  Kernel: {platform.uname().release}")
    print(f" 🌍  External IP Address: {get_external_ip()}")

    # WireGuard status
    print(f" 🛡️   WireGuard Status: {get_wireguard_status()}")
    config_path = "/etc/wireguard/wg0.conf"
    print(f" ⚙️   Config File: {config_path if os.path.exists(config_path) else colored('missing ❌', 'red')}")
    print(f" 🌐  Active peers: {get_wireguard_peers()}")

    # Last report
    report_path = os.path.join("pyWGgen", "test_report.txt")
    if os.path.exists(report_path):
        print(f" 📋  Last Report: {report_path}")
    else:
        print(colored(" 📋  Last Report: missing ❌", "red"))

    print("\n===========================================\n")

def generate_project_report():
    """Generates a full report."""
    print("\n  📋  Generating full report...")
    try:
        generate_report()
    except Exception as e:
        print(f" ❌ Error generating full report: {e}")

def display_test_report():
    """Displays the contents of the full report in the console."""
    if TEST_REPORT_PATH.exists():
        with open(TEST_REPORT_PATH, "r", encoding="utf-8") as file:
            print(file.read())
    else:
        print(f"  ❌  Full report file not found: {TEST_REPORT_PATH}")

def display_test_summary():
    """Displays a brief report."""
    if TEST_REPORT_PATH.exists():
        with open(TEST_REPORT_PATH, "r", encoding="utf-8") as file:
            lines = file.readlines()
            summary_keys = [
                "Date and Time",
                "WireGuard Status",
                "Gradio",
                "Open Ports",
                "wg0.conf"
            ]
            print("\n=== Brief Project Status Report ===")
            for line in lines:
                if any(key in line for key in summary_keys):
                    print(line.strip())
            print("\n=========================================")
    else:
        print(f"  ❌  Project status report file pyWGgen not found: {TEST_REPORT_PATH}")

def display_summary_report():
    """
    Reads and displays the content of the project status report pyWGgen.
    Uses the file path from settings.py.
    If the file is missing, initiates its creation.
    """
    try:
        if not SUMMARY_REPORT_PATH.exists():
            create_summary_report()

        with open(SUMMARY_REPORT_PATH, "r", encoding="utf-8") as file:
            content = file.read()

        print("\n=== 📋 Project Status Report pyWGgen ===\n")
        print(content)

    except Exception as e:
        print(f" ❌ Error reading project status report pyWGgen: {e}")

if __name__ == "__main__":
    show_project_status()
    time.sleep(2)
    print("\n=== Performing Report Operations ===\n")
    display_summary_report()
