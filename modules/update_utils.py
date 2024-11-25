#!/usr/bin/env python3
# modules/update_utils.py
# Модуль для обновления проекта и зависимостей

import subprocess

def update_project():
    """Обновление проекта и зависимостей."""
    print("  🔄  Обновление проекта и зависимостей...")
    subprocess.run(["git", "pull"])
    subprocess.run(["pip", "install", "-r", "requirements.txt"])
