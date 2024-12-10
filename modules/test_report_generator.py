#!/usr/bin/env python3
# modules/test_report_generator.py
# Скрипт для генерации полного отчета о состоянии проекта wg_qr_generator
# Версия: 2.1
# Обновлено: 2024-12-10
# Назначение: Генерация подробного отчета для диагностики состояния проекта.

import os
import json
import subprocess
import sys  # Добавлен импорт sys
from datetime import datetime
from pathlib import Path
from prettytable import PrettyTable

# Добавляем корневую директорию проекта в sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Импорт настроек
from settings import TEST_REPORT_PATH, USER_DB_PATH, WG_CONFIG_DIR, GRADIO_PORT


def load_json(filepath):
    """Загружает данные из JSON-файла."""
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return f" ❌  Файл {filepath} отсутствует."
    except json.JSONDecodeError:
        return f" ❌  Файл {filepath} поврежден."


def run_command(command):
    """Выполняет команду и возвращает вывод."""
    try:
        return subprocess.check_output(command, text=True).strip()
    except FileNotFoundError:
        return f" ❌  Команда '{command[0]}' не найдена."
    except subprocess.CalledProcessError as e:
        return f" ❌  Ошибка выполнения команды {' '.join(command)}: {e}"


def get_gradio_status():
    """Проверяет статус Gradio."""
    try:
        output = subprocess.check_output(["ps", "-eo", "pid,cmd"], text=True)
        for line in output.splitlines():
            if "gradio" in line and str(GRADIO_PORT) in line:
                return f" 🟢  Gradio запущен (строка: {line})"
        return " ❌  Gradio не запущен"
    except Exception as e:
        return f" ❌  Ошибка проверки Gradio: {e}"


def generate_report():
    """Генерация полного отчёта о состоянии проекта."""
    timestamp = datetime.utcnow().isoformat()
    user_records = load_json(USER_DB_PATH)

    report_lines = [f"\n === 📝  Отчет о состоянии проекта wg_qr_generator  ===", f" 📅  Дата и время: {timestamp}\n"]

    # Проверка структуры
    report_lines.append(" === 📂  Проверка структуры проекта  ===")
    required_files = {
        "user_records.json": USER_DB_PATH,
        "wg_configs": WG_CONFIG_DIR,
    }
    for name, path in required_files.items():
        report_lines.append(f"- {name}: {' 🟢  Присутствует' if Path(path).exists() else ' ❌  Отсутствует'}")

    required_dirs = ["logs", "user/data", "user/data/qrcodes", "user/data/wg_configs"]
    for folder in required_dirs:
        report_lines.append(f"- {folder}: {' 🟢  Существует' if os.path.exists(folder) else ' ❌  Отсутствует'}")

    # Данные из JSON
    report_lines.append("\n === 📄  Данные из user_records.json  ===")
    if isinstance(user_records, dict):
        table = PrettyTable(["Пользователь", "peer", "telegram_id"])
        for username, data in user_records.items():
            table.add_row([username, data.get('peer', 'N/A'), data.get('telegram_id', 'N/A')])
        report_lines.append(str(table))
    else:
        report_lines.append(f"{user_records}\n")

    # Проверка WireGuard
    report_lines.append("\n === 🔒  Результаты WireGuard (wg show)  ===")
    wg_show_output = run_command(["wg", "show"])
    report_lines.append(wg_show_output if wg_show_output else " ❌  WireGuard не запущен или ошибка.\n")

    # Проверка состояния WireGuard
    report_lines.append("\n === 🔧  Состояние WireGuard  ===")
    wg_status_output = run_command(["systemctl", "status", "wg-quick@wg0"])
    report_lines.append(wg_status_output)

    # Проверка открытых портов
    report_lines.append("\n === 🔍  Проверка открытых портов  ===")
    firewall_ports = run_command(["sudo", "firewall-cmd", "--list-ports"])
    report_lines.append(f"Открытые порты: {firewall_ports}")

    # Проверка Gradio
    report_lines.append("\n === 🌐  Статус Gradio  ===")
    gradio_status = get_gradio_status()
    report_lines.append(f"Gradio: {gradio_status}")

    # Проверка активных процессов
    report_lines.append("\n === 🖥️  Активные процессы  ===")
    try:
        ps_output = subprocess.check_output(["ps", "-eo", "pid,cmd"], text=True)
        report_lines.append(ps_output)
    except subprocess.CalledProcessError:
        report_lines.append(" ❌  Ошибка получения списка процессов.")

    # Сохранение отчёта
    with open(TEST_REPORT_PATH, "w", encoding="utf-8") as report_file:
        report_file.write("\n".join(report_lines))
    
    print(f"  ✅  Отчёт сохранён в:\n  📂 {TEST_REPORT_PATH}")


if __name__ == "__main__":
    generate_report()
