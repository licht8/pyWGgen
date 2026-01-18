#!/usr/bin/env python3
# gradio_admin/gradio_cli.py
# Skrypt do uruchamiania projektu przez emulację wiersza poleceń Gradio.

import os
import subprocess
from pathlib import Path
import sys

# Ścieżka do katalogu głównego projektu
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Ścieżka do aktywacji środowiska wirtualnego
VENV_ACTIVATE_PATH = PROJECT_ROOT / "venv/bin/activate"  # Dla Linux/macOS
# VENV_ACTIVATE_PATH = PROJECT_ROOT / "venv/Scripts/activate"  # Dla Windows

# Ścieżka do skryptu uruchamiającego projekt
RUN_PROJECT_SCRIPT = PROJECT_ROOT / "run_project.sh"

def run_project():
    """
    Uruchamia projekt przez ./run_project.sh, aktywując środowisko wirtualne.
    """
    if not RUN_PROJECT_SCRIPT.exists():
        return f"❌ Skrypt {RUN_PROJECT_SCRIPT} nie znaleziony. Upewnij się, że istnieje."
    
    if not VENV_ACTIVATE_PATH.exists():
        return f"❌ Środowisko wirtualne {VENV_ACTIVATE_PATH} nie znalezione. Sprawdź ścieżkę."

    try:
        # Polecenie do wykonania
        command = f"bash -c 'source {VENV_ACTIVATE_PATH} && {RUN_PROJECT_SCRIPT}'"

        # Wykonaj polecenie i zbierz wynik
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            return f"✅ Projekt pomyślnie uruchomiony!\n{result.stdout.strip()}"
        else:
            return f"❌ Błąd podczas uruchamiania projektu:\n{result.stderr.strip()}"

    except Exception as e:
        return f"❌ Wystąpił błąd: {str(e)}"

if __name__ == "__main__":
    # Uruchom projekt
    output = run_project()
    print(output)
