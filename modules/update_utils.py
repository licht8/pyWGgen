#!/usr/bin/env python3
# modules/update_utils.py
# Module for updating the project and dependencies

import subprocess

def update_project():
    """Updates the project and its dependencies."""
    print("  🔄  Updating project and dependencies...")
    subprocess.run(["git", "pull"])
    subprocess.run(["pip", "install", "-r", "requirements.txt"])
