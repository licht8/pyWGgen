#!/usr/bin/env python3
# debug_project.py
# Скрипт для диагностики и анализа структуры проекта wg_qr_generator.

import os
import sys
import json
import subprocess
from datetime import datetime
import threading
import time

EXCLUDE_DIRS = ['venv']  # Исключаем каталоги, которые не нужно сканировать (например, виртуальное окружение).
MAX_VISIBLE_FILES = 100  # Максимальное количество отображаемых файлов/папок в отчете

loading = False  # Глобальная переменная для управления лоадером

def start_loader(message="Processing"):
    """Функция запуска лоадера."""
    global loading
    loading = True
    spinner = ["|", "/", "-", "\\"]
    idx = 0
    while loading:
        print(f"\r{message} {spinner[idx % len(spinner)]}", end="", flush=True)
        idx += 1
        time.sleep(0.2)

def stop_loader():
    """Останавливает лоадер и очищает строку."""
    global loading
    loading = False
    print("\r", end="", flush=True)  # Удаляет лоадер с экрана

def log(message):
    """Логирует сообщение в консоль."""
    print(message)

def generate_project_structure_report(base_path, exclude_dirs, max_visible_files):
    """
    Генерация отчета о структуре проекта.
    :param base_path: Базовый путь проекта.
    :param exclude_dirs: Список директорий для исключения.
    :param max_visible_files: Максимальное количество файлов/папок для отображения.
    :return: Отчет о структуре в строковом формате.
    """
    report = ["=== Project Structure ==="]
    for root, dirs, files in os.walk(base_path):
        # Исключаем ненужные директории
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        relative_path = os.path.relpath(root, base_path)
        report.append(f"📂 {relative_path}")
        total_items = len(dirs) + len(files)

        # Сокращенное отображение папок с большим количеством файлов
        if total_items > max_visible_files:
            report.append(f"  ├── 📂 Contains {len(dirs)} folders and {len(files)} files")
        else:
            for d in dirs:
                report.append(f"  ├── 📂 {d}")
            for f in files:
                report.append(f"  ├── 📄 {f}")
    return "\n".join(report)

def debug_python_environment():
    """Отчет об окружении Python."""
    return f"""=== Python Environment ===
Python Executable: {sys.executable}
Python Version: {sys.version}
PYTHONPATH:
{sys.path}
"""

def debug_required_files_and_dirs(base_path):
    """Проверка необходимых файлов и директорий."""
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
            # Если отсутствует, создаем директорию или файл
            if "." not in os.path.basename(item):  # Если это директория
                os.makedirs(path, exist_ok=True)
                report.append(f"✅ Directory created: {item}")
            else:  # Если это файл
                with open(path, 'w') as f:
                    json.dump({}, f)
                report.append(f"✅ File created: {item}")
    return "\n".join(report)

def grep_functions_in_project(functions, base_path):
    """
    Поиск функций в проекте.
    :param functions: Список функций для поиска.
    :param base_path: Базовый путь проекта.
    :return: Словарь с результатами поиска.
    """
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
    """Форматирование отчета о найденных функциях."""
    report = ["=== Function Search Report ==="]
    for function, occurrences in function_occurrences.items():
        if occurrences:
            report.append(f"✅ {function} found in:")
            report.extend([f"  {line}" for line in occurrences])
        else:
            report.append(f"❌ {function} not found.")
    return "\n".join(report)

def main():
    """Основной процесс диагностики."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().isoformat()
    report_lines = [f"=== Diagnostic Report for wg_qr_generator ===", f"Timestamp: {timestamp}", ""]

    # Лоадер в отдельном потоке
    loader_thread = threading.Thread(target=start_loader, args=("Running diagnostics...",), daemon=True)
    loader_thread.start()

    try:
        # Отчет об окружении Python
        report_lines.append(debug_python_environment())

        # Проверка структуры проекта
        report_lines.append(generate_project_structure_report(base_path, EXCLUDE_DIRS, MAX_VISIBLE_FILES))

        # Проверка необходимых файлов/директорий
        report_lines.append(debug_required_files_and_dirs(base_path))

        # Поиск функций
        TARGET_FUNCTIONS = [
            "create_user_tab",
            "delete_user_tab",
            "statistics_tab",
            "run_gradio_admin_interface",
            "sync_users_with_wireguard",
        ]
        function_occurrences = grep_functions_in_project(TARGET_FUNCTIONS, base_path)
        report_lines.append(generate_function_search_report(function_occurrences))

    finally:
        # Остановить лоадер
        stop_loader()

    # Сохранение отчета
    report_path = os.path.join(base_path, "debug_report.txt")
    with open(report_path, "w") as report_file:
        report_file.write("\n".join(report_lines))
    
    log(f"✅ Отчет сохранен в {report_path}")

if __name__ == "__main__":
    main()
