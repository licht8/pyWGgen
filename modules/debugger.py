#!/usr/bin/env python3
# modules/debugger.py
# Модуль для диагностики проекта wg_qr_generator.

import os
import sys
import json
import subprocess
from datetime import datetime
import threading
import time

# Константы
EXCLUDE_DIRS = ['venv', '.pytest_cache', '.git', 'temp', '__pycache__']
MAX_VISIBLE_FILES = 100  # Максимальное количество файлов/папок в отчете
TARGET_FUNCTIONS = [
    "create_user_tab",
    "delete_user_tab",
    "statistics_tab",
    "run_gradio_admin_interface",
    "sync_users_with_wireguard",
]

# Глобальная переменная для лоадера
loading = False

def start_loader(message="Processing"):
    """Запускает лоадер."""
    global loading
    loading = True
    spinner = ["🌕", "🌖", "🌗", "🌘", "🌑", "🌒", "🌓", "🌔"]
    idx = 0
    while loading:
        print(f"\r{message} {spinner[idx % len(spinner)]}", end="", flush=True)
        idx += 1
        time.sleep(0.2)

def stop_loader():
    """Останавливает лоадер."""
    global loading
    loading = False
    print("\r", end="", flush=True)

def log(message):
    """Выводит сообщение в консоль."""
    print(message)

def generate_project_structure_report(base_path, exclude_dirs, max_visible_files):
    """Генерация отчета о структуре проекта."""
    report = ["=== Project Structure ==="]
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        relative_path = os.path.relpath(root, base_path)
        total_items = len(dirs) + len(files)

        if total_items > max_visible_files:
            report.append(f"📂 {relative_path} ─ {len(dirs)} folders, {len(files)} files")
        else:
            report.append(f"📂 {relative_path}")
            for d in dirs:
                report.append(f"  ├── 📂 {d}")
            for f in files:
                report.append(f"  ├── 📄 {f}")
    return "\n".join(report)

def debug_python_environment():
    """Создает отчет об окружении Python."""
    return f"""=== Python Environment ===
Python Executable: {sys.executable}
Python Version: {sys.version}
PYTHONPATH:
{sys.path}
"""

def debug_required_files_and_dirs(base_path):
    """Проверка наличия нужных файлов и директорий."""
    required_items = [
        "user/data/qrcodes",
        "user/data/wg_configs",
        "logs",
        "user/data/user_records.json",
        "logs/wg_users.json"
    ]
    report = ["=== Required Files/Dirs Check ==="]
    for item in required_items:
        path = os.path.join(base_path, item)
        if os.path.exists(path):
            report.append(f"✅ Exists: {item}")
        else:
            report.append(f"❌ Missing: {item}")
            if "." not in os.path.basename(item):
                os.makedirs(path, exist_ok=True)
                report.append(f"✅ Directory created: {item}")
            else:
                with open(path, 'w') as f:
                    json.dump({}, f)
                report.append(f"✅ File created: {item}")
    return "\n".join(report)

def grep_functions_in_project(functions, base_path):
    """Поиск функций в проекте."""
    function_occurrences = {}
    for function in functions:
        command = f"grep -r -n -E 'def {function}\\(' {base_path}"
        try:
            output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)
            function_occurrences[function] = output.strip().splitlines()
        except subprocess.CalledProcessError:
            function_occurrences[function] = []
    return function_occurrences

def generate_function_search_report(function_occurrences):
    """Создание отчета о найденных функциях."""
    report = ["=== Function Search Report ==="]
    for function, occurrences in function_occurrences.items():
        if occurrences:
            report.append(f"✅ {function} found in:")
            report.extend([f"  {line}" for line in occurrences])
        else:
            report.append(f"❌ {function} not found.")
    return "\n".join(report)

def run_diagnostics():
    """Основной процесс диагностики."""
    base_path = os.path.abspath(os.path.join(__file__, "../../"))
    timestamp = datetime.now().isoformat()
    report_lines = [f"=== Diagnostic Report for wg_qr_generator ===", f"Timestamp: {timestamp}", ""]

    loader_thread = threading.Thread(target=start_loader, args=("Running diagnostics...",), daemon=True)
    loader_thread.start()

    try:
        report_lines.append(debug_python_environment())
        report_lines.append(generate_project_structure_report(base_path, EXCLUDE_DIRS, MAX_VISIBLE_FILES))
        report_lines.append(debug_required_files_and_dirs(base_path))
        function_occurrences = grep_functions_in_project(TARGET_FUNCTIONS, base_path)
        report_lines.append(generate_function_search_report(function_occurrences))
    finally:
        stop_loader()

    report_path = os.path.join(base_path, "modules", "debug_report.txt")
    with open(report_path, "w") as report_file:
        report_file.write("\n".join(report_lines))
    log(f"✅ Отчет сохранен в {report_path}")

if __name__ == "__main__":
    run_diagnostics()
