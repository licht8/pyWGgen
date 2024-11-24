#!/usr/bin/env python3
# test_report_generator.py
# Скрипт для тестирования системы wg_qr_generator и генерации отчета

import os
import json
import subprocess
from datetime import datetime

# Пути к файлам
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
USER_RECORDS_PATH = os.path.join(PROJECT_ROOT, "user", "data", "user_records.json")
WG_USERS_PATH = os.path.join(LOGS_DIR, "wg_users.json")
REPORT_FILE = os.path.join(PROJECT_ROOT, "test_report.txt")

def run_command(command):
    """Выполняет команду в shell и возвращает результат."""
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        return f"Ошибка выполнения команды '{command}': {e}"

def load_json(filepath):
    """Загружает данные из JSON-файла."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "Файл не найден"}
    except json.JSONDecodeError as e:
        return {"error": f"Ошибка декодирования JSON: {e}"}

def analyze_field_presence(data, fields):
    """
    Проверяет наличие и заполненность указанных полей в данных.
    :param data: Данные для анализа (словарь)
    :param fields: Список ключей для проверки
    :return: Строка отчета
    """
    report = []
    for username, user_data in data.items():
        report.append(f"Пользователь: {username}")
        for field in fields:
            value = user_data.get(field, "N/A")
            status = "Заполнено" if value != "N/A" else "Пусто"
            report.append(f"  {field}: {value} ({status})")
        report.append("")
    return "\n".join(report)

def write_report(content):
    """Записывает отчет в файл."""
    with open(REPORT_FILE, "w") as f:
        f.write(content)
    print(f"✅ Отчет сохранен в {REPORT_FILE}")

def main():
    report = []
    report.append(f"=== Отчет о тестировании wg_qr_generator ===")
    report.append(f"Дата и время: {datetime.now().isoformat()}")
    report.append("")

    # 1. Проверка существования важных файлов
    report.append("=== Проверка файлов ===")
    report.append(f"- Путь к user_records.json: {USER_RECORDS_PATH}")
    report.append(f"- Путь к wg_users.json: {WG_USERS_PATH}")
    report.append(f"- user_records.json существует: {'Да' if os.path.exists(USER_RECORDS_PATH) else 'Нет'}")
    report.append(f"- wg_users.json существует: {'Да' if os.path.exists(WG_USERS_PATH) else 'Нет'}")
    report.append("")

    # 2. Проверка данных в user_records.json
    report.append("=== Данные из user_records.json ===")
    user_records = load_json(USER_RECORDS_PATH)
    if "error" in user_records:
        report.append(f"Ошибка: {user_records['error']}")
    else:
        report.append(json.dumps(user_records, indent=4))
        report.append("\n--- Анализ полей (peer, telegram_id) в user_records.json ---")
        report.append(analyze_field_presence(user_records, ["peer", "telegram_id"]))

    report.append("")

    # 3. Проверка данных в wg_users.json
    report.append("=== Данные из wg_users.json ===")
    wg_users = load_json(WG_USERS_PATH)
    if "error" in wg_users:
        report.append(f"Ошибка: {wg_users['error']}")
    else:
        report.append(json.dumps(wg_users, indent=4))
        report.append("\n--- Анализ полей (peer, telegram_id) в wg_users.json ---")
        report.append(analyze_field_presence(wg_users, ["peer", "telegram_id"]))

    report.append("")

    # 4. Проверка команды wg show
    report.append("=== Результаты wg show ===")
    wg_show = run_command("wg show")
    report.append(wg_show)
    report.append("")

    # 5. Проверка запуска Gradio
    report.append("=== Проверка Gradio ===")
    gradio_check = run_command("ps aux | grep '[p]ython3.*menu.py'")
    report.append(f"Gradio запущен: {'Да' if gradio_check else 'Нет'}")
    report.append("")

    # 6. Проверка состояния WireGuard
    report.append("=== Состояние WireGuard ===")
    wireguard_status = run_command("systemctl status wg-quick@wg0 --no-pager")
    report.append(wireguard_status)
    report.append("")

    # Запись отчета в файл
    write_report("\n".join(report))

if __name__ == "__main__":
    main()
