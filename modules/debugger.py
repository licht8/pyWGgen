#!/usr/bin/env python3
# modules/debugger.py
# Модуль для диагностики проекта wg_qr_generator.

import os
import sys
import subprocess
from datetime import datetime
import threading
import time

EXCLUDE_DIRS = ['venv', '.pytest_cache', '.git', 'temp', '__pycache__']
TARGET_FUNCTIONS = [
    "create_user_tab",
    "delete_user_tab",
    "statistics_tab",
    "run_gradio_admin_interface",
    "sync_users_with_wireguard",
]

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

def summarize_project_structure(base_path, exclude_dirs):
    """Возвращает краткий обзор структуры проекта."""
    directories = []
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        if root == base_path:
            directories = dirs
            break
    return f"Root Directory: {base_path}\nKey Directories:\n" + "\n".join([f"- {d}" for d in directories])

def debug_python_environment():
    """Создает отчет об окружении Python."""
    return f"""=== Python Environment ===
Python Executable: {sys.executable}
Python Version: {sys.version.split()[0]}
PYTHONPATH: {sys.path[:1]}...
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
    status = []
    for item in required_items:
        path = os.path.join(base_path, item)
        if os.path.exists(path):
            status.append(f"✅ {item}")
        else:
            status.append(f"❌ {item}")
    return "=== Required Files/Dirs Status ===\n" + "\n".join(status)

def grep_functions_in_project(functions, base_path):
    """Поиск функций в проекте."""
    function_occurrences = {}
    for function in functions:
        command = f"grep -r -n -E '\\bdef\\s+{function}\\b' {base_path}"  # Точное соответствие имени функции
        try:
            output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)
            function_occurrences[function] = output.strip().splitlines()
        except subprocess.CalledProcessError:
            function_occurrences[function] = []
    return function_occurrences

def generate_function_search_summary(function_occurrences):
    """Создает краткое резюме поиска функций."""
    summary = []
    for function, occurrences in function_occurrences.items():
        if occurrences:
            summary.append(f"✅ {function}: Found in {occurrences[0].split(':')[0]}")
        else:
            summary.append(f"❌ {function}: Not found.")
    return "=== Function Search Summary ===\n" + "\n".join(summary)

def run_diagnostics():
    """Основной процесс диагностики."""
    base_path = os.path.abspath(os.path.join(__file__, "../../"))  # Корень проекта
    timestamp = datetime.now().isoformat()
    report_lines = [f"=== Diagnostic Report for wg_qr_generator ===", f"Timestamp: {timestamp}", ""]

    loader_thread = threading.Thread(target=start_loader, args=("Running diagnostics...",), daemon=True)
    loader_thread.start()

    try:
        report_lines.append(debug_python_environment())
        report_lines.append(summarize_project_structure(base_path, EXCLUDE_DIRS))
        report_lines.append(debug_required_files_and_dirs(base_path))
        function_occurrences = grep_functions_in_project(TARGET_FUNCTIONS, base_path)
        report_lines.append(generate_function_search_summary(function_occurrences))
    finally:
        stop_loader()

    report_path = os.path.join(base_path, "modules", "debug_report.txt")
    with open(report_path, "w") as report_file:
        report_file.write("\n".join(report_lines))
    log(f"✅ Отчет сохранен в {report_path}")

if __name__ == "__main__":
    run_diagnostics()
