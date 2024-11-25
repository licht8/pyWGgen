#!/usr/bin/env python3
# test_report_generator.py
# Скрипт для генерации отчета о состоянии проекта wg_qr_generator

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
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def run_command(command):
    """Выполняет команду и возвращает вывод."""
    try:
        return subprocess.check_output(command, text=True).strip()
    except subprocess.CalledProcessError as e:
        return f"Ошибка выполнения команды: {e}"

def generate_report():
    """Генерирует отчет о состоянии проекта."""
    timestamp = datetime.utcnow().isoformat()
    user_records = load_json(USER_RECORDS_JSON)
    wg_users = load_json(WG_USERS_JSON)

    report_lines = [f"=== Отчет о тестировании wg_qr_generator ===", f"Дата и время: {timestamp}\n"]

    # Проверка файлов
    report_lines.append("=== Проверка файлов ===")
    report_lines.append(f"- Путь к user_records.json: {USER_RECORDS_JSON}")
    report_lines.append(f"- Путь к wg_users.json: {WG_USERS_JSON}")
    report_lines.append(f"- user_records.json существует: {'Да' if os.path.exists(USER_RECORDS_JSON) else 'Нет'}")
    report_lines.append(f"- wg_users.json существует: {'Да' if os.path.exists(WG_USERS_JSON) else 'Нет'}")
    report_lines.append(f"- wg0.conf существует: {'Да' if os.path.exists(WG_CONFIG) else 'Нет'}\n")

    # Данные JSON
    report_lines.append("=== Данные из user_records.json ===")
    report_lines.append(json.dumps(user_records, indent=4) if user_records else "Нет данных.\n")

    report_lines.append("--- Анализ user_records.json ---")
    for username, data in user_records.items():
        report_lines.append(f"Пользователь: {username}")
        report_lines.append(f"  peer: {data.get('peer', 'N/A')}")
        report_lines.append(f"  telegram_id: {data.get('telegram_id', 'N/A')}\n")

    report_lines.append("=== Данные из wg_users.json ===")
    report_lines.append(json.dumps(wg_users, indent=4) if wg_users else "Нет данных.\n")

    # Проверка WireGuard
    report_lines.append("=== Результаты wg show ===")
    report_lines.append(run_command(["wg", "show"]) or "WireGuard не запущен или ошибка.")

    # Проверка состояния WireGuard
    report_lines.append("=== Состояние WireGuard ===")
    report_lines.append(run_command(["systemctl", "status", "wg-quick@wg0"]))

    # Проверка структуры папок
    report_lines.append("\n=== Структура папок ===")
    required_dirs = ["logs", "user/data", "user/data/qrcodes", "user/data/wg_configs"]
    for folder in required_dirs:
        report_lines.append(f"- {folder}: {'Существует' if os.path.exists(folder) else 'Отсутствует'}")

    # Сохранение отчета
    with open(TEST_REPORT_PATH, "w") as report_file:
        report_file.write("\n".join(report_lines))
    
    print(f"✅ Отчет сохранен в {TEST_REPORT_PATH}")

if __name__ == "__main__":
    generate_report()
