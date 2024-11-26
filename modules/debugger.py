#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debugger Module for wg_qr_generator
===================================
This module generates a diagnostic report to help identify potential
issues within the project structure, dependencies, and functionality.

Author: [Your Name]
Date: [Today's Date]
"""

import os
import sys
import json
import datetime
from pathlib import Path

# Constants
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_ROOT / "modules" / "debug_report.txt"
ICONS = {
    "dir": "📂",
    "file": "📄",
    "check": "✅",
    "cross": "❌"
}

# Function to gather Python environment details
def get_python_environment():
    """
    Collect details about the current Python environment.
    """
    return {
        "Python Executable": sys.executable,
        "Python Version": sys.version,
        "PYTHONPATH": sys.path,
    }

# Function to collect project structure
def get_project_structure(root_dir):
    """
    Generate a structured representation of the project directory.
    """
    structure = []
    for root, dirs, files in os.walk(root_dir):
        depth = root.replace(str(root_dir), "").count(os.sep)
        indent = "  " * depth
        structure.append(f"{indent}{ICONS['dir']} {os.path.basename(root)}")
        subindent = "  " * (depth + 1)
        for f in files:
            structure.append(f"{subindent}{ICONS['file']} {f}")
    return "\n".join(structure)

# Function to verify required files and directories
def check_required_items(required_items):
    """
    Check the existence of required files and directories.
    """
    results = {}
    for item in required_items:
        results[item] = ICONS["check"] if Path(item).exists() else ICONS["cross"]
    return results

# Function to search for specific functions
def search_functions_in_files(functions, root_dir):
    """
    Search for specific function definitions across the project files.
    """
    results = {func: [] for func in functions}
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    for func in functions:
                        if f"def {func}(" in line:
                            results[func].append(f"{os.path.join(root, file)}:{i + 1}")
    return results

# Function to write the report
def write_report(report_data, output_file):
    """
    Write the generated diagnostic report to a file.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_data)

# Main diagnostic function
def run_diagnostics():
    """
    Main function to generate and write the diagnostic report.
    """
    timestamp = datetime.datetime.now().isoformat()
    required_items = [
        "user/data/qrcodes",
        "user/data/wg_configs",
        "logs",
        "user/data/user_records.json",
        "logs/wg_users.json"
    ]
    functions_to_search = [
        "create_user_tab",
        "delete_user_tab",
        "statistics_tab",
        "run_gradio_admin_interface",
        "sync_users_with_wireguard"
    ]

    # Collect data
    python_env = get_python_environment()
    project_structure = get_project_structure(PROJECT_ROOT)
    required_checks = check_required_items(required_items)
    function_search_results = search_functions_in_files(functions_to_search, PROJECT_ROOT)

    # Generate report
    report = [
        f"=== Diagnostic Report for wg_qr_generator ===",
        f"Timestamp: {timestamp}",
        "",
        "=== Python Environment ===",
        "\n".join([f"{key}: {value}" for key, value in python_env.items()]),
        "",
        "=== Project Structure ===",
        project_structure,
        "",
        "=== Required Files/Dirs Status ===",
        "\n".join([f"{ICONS['check'] if status == ICONS['check'] else ICONS['cross']} {item}" for item, status in required_checks.items()]),
        "",
        "=== Function Search Summary ===",
        "\n".join([f"{ICONS['check']} {func}: Found in {', '.join(locations) if locations else 'Not found'}" for func, locations in function_search_results.items()]),
    ]
    report_data = "\n".join(report)

    # Write to file
    write_report(report_data, REPORT_FILE)
    print(f"Diagnostic report written to {REPORT_FILE}")
