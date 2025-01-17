#!/usr/bin/env python3
# gradio_admin/gradio_cli.py
# Script for launching the project via Gradio's command-line emulation.

import os
import subprocess
from pathlib import Path
import sys

# Path to the project's root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Path to the virtual environment
VENV_ACTIVATE_PATH = PROJECT_ROOT / "venv/bin/activate"  # For Linux/macOS
# VENV_ACTIVATE_PATH = PROJECT_ROOT / "venv/Scripts/activate"  # For Windows

# Path to the project launch script
RUN_PROJECT_SCRIPT = PROJECT_ROOT / "run_project.sh"

def run_project():
    """
    Executes the project launch via ./run_project.sh, activating the virtual environment.
    """
    if not RUN_PROJECT_SCRIPT.exists():
        return f"❌ Script {RUN_PROJECT_SCRIPT} not found. Ensure it exists."
    
    if not VENV_ACTIVATE_PATH.exists():
        return f"❌ Virtual environment {VENV_ACTIVATE_PATH} not found. Check the path."

    try:
        # Command to execute
        command = f"bash -c 'source {VENV_ACTIVATE_PATH} && {RUN_PROJECT_SCRIPT}'"

        # Execute the command and collect the result
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            return f"✅ Project successfully launched!\n{result.stdout.strip()}"
        else:
            return f"❌ Error while launching the project:\n{result.stderr.strip()}"

    except Exception as e:
        return f"❌ An error occurred: {str(e)}"

if __name__ == "__main__":
    # Execute the project launch
    output = run_project()
    print(output)
