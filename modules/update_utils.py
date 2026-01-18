#!/usr/bin/env python3
# modules/update_utils.py
# Moduł do aktualizacji projektu i zależności

import subprocess

def update_project():
    """
    Aktualizuje projekt i jego zależności.
    """
    print("  🔄  Aktualizacja projektu i zależności...")
    subprocess.run(["git", "pull"])
    subprocess.run(["pip", "install", "-r", "requirements.txt"])
