#!/usr/bin/env python3
# gradio_admin/gradio_cli.py
# Скрипт для запуска проекта через эмуляцию командной строки Gradio.

import os
import subprocess
from pathlib import Path
import sys

# Путь к корневой директории проекта
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Путь к виртуальному окружению
VENV_ACTIVATE_PATH = PROJECT_ROOT / "venv/bin/activate"  # Для Linux/macOS
# VENV_ACTIVATE_PATH = PROJECT_ROOT / "venv/Scripts/activate"  # Для Windows

# Путь к скрипту запуска проекта
RUN_PROJECT_SCRIPT = PROJECT_ROOT / "run_project.sh"

def run_project():
    """
    Выполняет запуск проекта через ./run_project.sh, активируя виртуальное окружение.
    """
    if not RUN_PROJECT_SCRIPT.exists():
        return f"❌ Скрипт {RUN_PROJECT_SCRIPT} не найден. Убедитесь, что он существует."
    
    if not VENV_ACTIVATE_PATH.exists():
        return f"❌ Виртуальное окружение {VENV_ACTIVATE_PATH} не найдено. Проверьте корректность пути."

    try:
        # Команды для выполнения
        command = f"bash -c 'source {VENV_ACTIVATE_PATH} && {RUN_PROJECT_SCRIPT}'"

        # Выполняем команду и собираем результат
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            return f"✅ Проект успешно запущен!\n{result.stdout.strip()}"
        else:
            return f"❌ Ошибка при запуске проекта:\n{result.stderr.strip()}"

    except Exception as e:
        return f"❌ Произошла ошибка: {str(e)}"

if __name__ == "__main__":
    # Выполняем запуск проекта
    output = run_project()
    print(output)
