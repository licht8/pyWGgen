#!/usr/bin/env python3
# modules/debugger.py
# -*- coding: utf-8 -*-
"""
Moduł debugera dla pyWGgen
===================================
Ten moduł generuje raport diagnostyczny pomagający zidentyfikować potencjalne
problemy ze strukturą projektu, zależnościami i funkcjonalnością.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Dodajemy katalog główny projektu do sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from settings import DIAGNOSTICS_LOG

EXCLUDE_DIRS = ['venv', '.pytest_cache', '.git', 'temp', '__pycache__']
MAX_VISIBLE_FILES = 100
ICONS = {
    "dir": " 📂",
    "file": " 📄",
    "check": " ✅",
    "cross": " ❌"
}


def get_python_environment():
    """Pobiera informacje o środowisku Python."""
    return {
        "Ścieżka Python": sys.executable,
        "Wersja Python": sys.version,
        "PYTHONPATH": sys.path,
    }


def get_project_structure(root_dir, exclude_dirs, max_visible_files):
    """Analizuje strukturę projektu."""
    structure = ["=== Struktura projektu ==="]
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        relative_path = os.path.relpath(root, root_dir)
        structure.append(f"{ICONS['dir']} {relative_path}")
        total_items = len(dirs) + len(files)

        if total_items > max_visible_files:
            structure.append(f"  ├── 📂 Zawiera {len(dirs)} folderów i {len(files)} plików")
        else:
            for d in dirs:
                structure.append(f"  ├── {ICONS['dir']} {d}")
            for f in files:
                structure.append(f"  ├── {ICONS['file']} {f}")
    return "\n".join(structure)


def check_required_items(required_items):
    """Sprawdza wymagane elementy projektu."""
    results = []
    for item in required_items:
        item_path = PROJECT_ROOT / item
        if item_path.exists():
            results.append(f"{ICONS['check']} Istnieje: {item}")
        else:
            results.append(f"{ICONS['cross']} Brakuje: {item}")
            if item_path.suffix:
                item_path.parent.mkdir(parents=True, exist_ok=True)
                item_path.write_text("{}")
                results.append(f"{ICONS['check']} Plik utworzony: {item}")
            else:
                item_path.mkdir(parents=True, exist_ok=True)
                results.append(f"{ICONS['check']} Katalog utworzony: {item}")
    return "\n".join(results)


def write_report(report_data, output_file):
    """Zapisuje raport diagnostyczny."""
    os.makedirs(output_file.parent, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_data)


def run_diagnostics():
    """Uruchamia pełną diagnostykę projektu."""
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

    python_env = get_python_environment()
    project_structure = get_project_structure(PROJECT_ROOT, EXCLUDE_DIRS, MAX_VISIBLE_FILES)
    required_checks = check_required_items(required_items)

    report = [
        f"=== Raport diagnostyczny ===",
        f"Data i czas: {timestamp}",
        "",
        "=== Środowisko Python ===",
        "\n".join([f"{key}: {value}" for key, value in python_env.items()]),
        "",
        project_structure,
        "",
        "=== Status wymaganych plików/katalogów ===",
        required_checks
    ]
    report_data = "\n".join(report)
    write_report(report_data, DIAGNOSTICS_LOG)
    print(f"  ✅  Raport zapisany w:\n 📂  {DIAGNOSTICS_LOG}")


if __name__ == "__main__":
    run_diagnostics()
