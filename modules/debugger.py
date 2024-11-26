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
from datetime import datetime
from pathlib import Path

# Constants
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_ROOT / "modules" / "debug_report.txt"
EXCLUDE_DIRS = ['venv', '.pytest_cache', '.git', 'temp', '__pycache__']
MAX_VISIBLE_FILES = 100  # Maximum files/folders visible in the structure report
ICONS = {
    "dir": "📂",
    "file": "📄",
    "check": "✅",
    "cross": "❌"
}


# Function to collect Python environment details
def get_python_environment():
    """
    Collect details about the current Python environment.
    """
    return {
        "Python Executable": sys.executable,
        "Python Version": sys.version,
        "PYTHONPATH": sys.path,
    }


# Function to collect project structure, with excluded directories
def get_project_structure(root_dir, exclude_dirs, max_visible_files):
    """
    Generate a structured representation of the project directory.
    Excludes specified directories from the structure report.
    """
    structure = ["=== Project Structure ==="]
    for root, dirs, files in os.walk(root_dir):
        # Exclude unwanted directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        relative_path = os.path.relpath(root, root_dir)
        structure.append(f"{ICONS['dir']} {relative_path}")
        total_items = len(dirs) + len(files)

        # Truncate display for large directories
        if total_items > max_visible_files:
            structure.append(f"  ├── 📂 Contains {len(dirs)} folders and {len(files)} files")
        else:
            for d in dirs:
                structure.append(f"  ├── {ICONS['dir']} {d}")
            for f in files:
                structure.append(f"  ├── {ICONS['file']} {f}")
    return "\n".join(structure)


# Function to verify required files and directories
def check_required_items(required_items):
    """
    Check the existence of required files and directories.
    """
    results = []
    for item in required_items:
        item_path = PROJECT_ROOT / item
        if item_path.exists():
            results.append(f"{ICONS['check']} Exists: {item}")
        else:
            results.append(f"{ICONS['cross']} Missing: {item}")
            # Create missing directories or files
            if item_path.suffix:  # It's a file
                item_path.parent.mkdir(parents=True, exist_ok=True)
                item_path.write_text("{}")  # Create an empty JSON file
                results.append(f"{ICONS['check']} File created: {item}")
            else:  # It's a directory
                item_path.mkdir(parents=True, exist_ok=True)
                results.append(f"{ICONS['check']} Directory created: {item}")
    return "\n".join(results)


# Function to search for specific functions in project files
def search_functions_in_files(functions, root_dir):
    """
    Search for specific function definitions across the project files.
    """
    results = {func: [] for func in functions}
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    for func in functions:
                        if f"def {func}(" in line:
                            results[func].append(f"{file_path}:{i + 1}")
    return results


# Function to write the diagnostic report
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
    timestamp = datetime.now().isoformat()
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
    project_structure = get_project_structure(PROJECT_ROOT, EXCLUDE_DIRS, MAX_VISIBLE_FILES)
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
        project_structure,
        "",
        "=== Required Files/Dirs Status ===",
        required_checks,
        "",
        "=== Function Search Report ===",
        "\n".join([
            f"{ICONS['check']} {func} found in:\n  " + "\n  ".join(locations) if locations else f"{ICONS['cross']} {func} not found."
            for func, locations in function_search_results.items()
        ])
    ]
    report_data = "\n".join(report)

    # Write to file
    write_report(report_data, REPORT_FILE)
    print(f"Diagnostic report written to {REPORT_FILE}")


# Run diagnostics when executed as a script
if __name__ == "__main__":
    run_diagnostics()
