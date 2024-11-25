#!/usr/bin/env python3
# test_report_generator.py
# Скрипт для генерации отчета о состоянии проекта wg_qr_generator
# Версия: 1.2
# Обновлено: 2024-11-25
# Автор: Ваше Имя

import os
import json
import subprocess
from datetime import datetime

# Пути к файлам
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
USER_RECORDS_JSON = os.path.join(BASE_DIR, "user/data/user_records.json")
WG_USERS_JSON = os.path.join(BASE_DIR, "logs/wg_users.json")
TEST_REPORT_PATH = os.path.join(BASE_DIR, "test_report.txt")
WG_CONFIG = "/etc/wireguard/wg0.conf"

def load_json(filepath):
    """Загружает данные из JSON-файла."""
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return f"Файл {filepath} отсутствует."
    except json.JSONDecodeError:
        return f"Файл {filepath} поврежден."

def run_command(command):
    """Выполняет команду и возвращает вывод."""
    try:
        return subprocess.check_output(command, text=True).strip()
    except subprocess.CalledProcessError as e:
        return f"Ошибка выполнения команды {' '.join(command)}: {e}"

def generate_report():
    """Генерирует отчет о состоянии проекта."""
    timestamp = datetime.utcnow().isoformat()
    user_records = load_json(USER_RECORDS_JSON)
    wg_users = load_json(WG_USERS_JSON)

    report_lines = [f"=== Отчет о тестировании wg_qr_generator ===", f"Дата и время: {timestamp}\n"]

    # Проверка структуры проекта
    report_lines.append("=== Проверка структуры проекта ===")
    required_files = {
        "user_records.json": USER_RECORDS_JSON,
        "wg_users.json": WG_USERS_JSON,
        "wg0.conf": WG_CONFIG
    }
    for name, path in required_files.items():
        report_lines.append(f"- {name}: {'Присутствует' if os.path.exists(path) else 'Отсутствует'}")
    
    required_dirs = ["logs", "user/data", "user/data/qrcodes", "user/data/wg_configs"]
    for folder in required_dirs:
        report_lines.append(f"- {folder}: {'Существует' if os.path.exists(folder) else 'Отсутствует'}")

    # Данные из JSON
    report_lines.append("\n=== Данные из user_records.json ===")
    if isinstance(user_records, dict):
        report_lines.append(json.dumps(user_records, indent=4))
    else:
        report_lines.append(f"{user_records}\n")

    report_lines.append("--- Анализ user_records.json ---")
    if isinstance(user_records, dict):
        for username, data in user_records.items():
            report_lines.append(f"Пользователь: {username}")
            report_lines.append(f"  peer: {data.get('peer', 'N/A')}")
            report_lines.append(f"  telegram_id: {data.get('telegram_id', 'N/A')}\n")

    report_lines.append("=== Данные из wg_users.json ===")
    if isinstance(wg_users, dict):
        report_lines.append(json.dumps(wg_users, indent=4))
    else:
        report_lines.append(f"{wg_users}\n")

    # Проверка WireGuard
    report_lines.append("=== Результаты wg show ===")
    wg_show_output = run_command(["wg", "show"])
    report_lines.append(wg_show_output if wg_show_output else "WireGuard не запущен или ошибка.\n")

    report_lines.append("=== Состояние WireGuard ===")
    wg_status_output = run_command(["systemctl", "status", "wg-quick@wg0"])
    report_lines.append(wg_status_output)

    # Проверка портов
    report_lines.append("\n=== Проверка открытых портов ===")
    firewall_ports = run_command(["sudo", "firewall-cmd", "--list-ports"])
    report_lines.append(f"Открытые порты: {firewall_ports}")

    # Проверка Gradio
    report_lines.append("\n=== Статус Gradio ===")
    gradio_status = run_command(["ps", "aux", "|", "grep", "gradio"])
    report_lines.append(f"Процессы Gradio: {gradio_status}")

    # Сохранение отчета
    with open(TEST_REPORT_PATH, "w") as report_file:
        report_file.write("\n".join(report_lines))
    
    print(f"✅ Отчет сохранен в {TEST_REPORT_PATH}")

if __name__ == "__main__":
    generate_report()
