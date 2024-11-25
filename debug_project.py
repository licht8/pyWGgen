#!/usr/bin/env python3
# debug_project.py
# Скрипт для отладки проекта wg_qr_generator

import os
import subprocess
import sys
import json
from datetime import datetime


# Настройки
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TARGET_FUNCTIONS = [
    "create_user_tab",
    "delete_user_tab",
    "statistics_tab",
    "run_gradio_admin_interface",
    "sync_users_with_wireguard"
]
REQUIRED_PATHS = [
    "user/data/qrcodes",
    "user/data/wg_configs",
    "logs",
]
REQUIRED_FILES = {
    "user/data/user_records.json": "{}",
    "logs/wg_users.json": "{}"
}
REPORT_PATH = os.path.join(PROJECT_ROOT, "debug_report.txt")


# Вспомогательные функции
def write_json(file_path, data):
    """Запись данных в JSON-файл."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def create_missing_files_and_dirs():
    """Создает недостающие файлы и директории."""
    report_lines = ["=== Missing Files/Dirs Creation ==="]
    for path in REQUIRED_PATHS:
        full_path = os.path.join(PROJECT_ROOT, path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            report_lines.append(f"✅ Directory created: {path}")
    for file_path, default_content in REQUIRED_FILES.items():
        full_path = os.path.join(PROJECT_ROOT, file_path)
        if not os.path.exists(full_path):
            with open(full_path, "w", encoding="utf-8") as file:
                file.write(default_content)
            report_lines.append(f"✅ File created: {file_path}")
    return report_lines


def check_required_files_and_dirs():
    """Проверяет наличие необходимых файлов и директорий."""
    report_lines = ["=== Required Files/Dirs Check ==="]
    for path in REQUIRED_PATHS:
        full_path = os.path.join(PROJECT_ROOT, path)
        if os.path.exists(full_path):
            report_lines.append(f"✅ Directory exists: {path}")
        else:
            report_lines.append(f"❌ Missing directory: {path}")
    for file_path in REQUIRED_FILES.keys():
        full_path = os.path.join(PROJECT_ROOT, file_path)
        if os.path.exists(full_path):
            report_lines.append(f"✅ File exists: {file_path}")
        else:
            report_lines.append(f"❌ Missing file: {file_path}")
    return report_lines


def grep_functions_in_project(functions, timeout=10):
    """Ищет функции по всему проекту с ограничением времени."""
    report_lines = ["=== Function Search Report ==="]
    try:
        command = f"grep -r -n -E {'|'.join(functions)} {PROJECT_ROOT}"
        output = subprocess.check_output(command, shell=True, text=True, timeout=timeout)
        report_lines.append(output.strip())
    except subprocess.TimeoutExpired:
        report_lines.append("❌ Timeout expired during function search.")
    except Exception as e:
        report_lines.append(f"❌ Error during function search: {e}")
    return report_lines


def run_diagnostics():
    """Запускает все проверки и возвращает отчет."""
    report_lines = [
        f"=== Diagnostic Report for wg_qr_generator ===",
        f"Timestamp: {datetime.now().isoformat()}",
        ""
    ]

    # Проверка Python окружения
    report_lines.append("=== Python Environment ===")
    report_lines.append(f"Python Executable: {sys.executable}")
    report_lines.append(f"Python Version: {sys.version}")
    report_lines.append(f"PYTHONPATH:\n{sys.path}\n")

    # Проверка структуры проекта
    report_lines.append("=== Project Structure Check ===")
    report_lines.extend(check_required_files_and_dirs())

    # Создание недостающих файлов/директорий
    report_lines.extend(create_missing_files_and_dirs())

    # Проверка функций
    report_lines.extend(grep_functions_in_project(TARGET_FUNCTIONS))

    return report_lines


def save_report(report_lines):
    """Сохраняет отчет в файл."""
    with open(REPORT_PATH, "w", encoding="utf-8") as report_file:
        report_file.write("\n".join(report_lines))
    print(f"✅ Отчет сохранен в {REPORT_PATH}")


# Основная логика
def main():
    report_lines = run_diagnostics()
    save_report(report_lines)


if __name__ == "__main__":
    main()
