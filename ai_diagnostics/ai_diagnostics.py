#!/usr/bin/env python3
# ai_diagnostics/ai_diagnostics.py
# Скрипт для диагностики и анализа состояния проекта wg_qr_generator.
# Генерирует отчёты и анализирует их, предоставляя рекомендации по исправлению проблем.
# Версия: 2.8
# Обновлено: 2024-11-29

import json
import time
import sys
import subprocess
import random
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Импорт настроек
from settings import DEBUG_REPORT_PATH, TEST_REPORT_PATH, MESSAGES_DB_PATH


def run_command(command):
    """Запускает внешнюю команду и возвращает её результат."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Ошибка: {e.stderr.strip()}"


def animate_message(message):
    """Выводит анимированное сообщение с эффектом перемигивания '...'. Время перемигивания до 2 секунд."""
    for _ in range(3):  # Три итерации перемигивания
        for dots in range(1, 4):
            print(f"\r   {message}{'.' * dots}{' ' * (3 - dots)}", end="", flush=True)
            time.sleep(random.uniform(0.2, 0.5))  # Задержка от 0.2 до 0.5 секунд
    print(f"\r   {message} 🤖", flush=True)  # Завершающее сообщение с иконкой


def generate_debug_report():
    """Запускает дебаггер для создания свежего debug_report.txt."""
    print("\n")  # Добавлена строка перед генерацией
    animate_message("🤖  Генерация отчёта диагностики")
    command = [sys.executable, PROJECT_ROOT / "modules" / "debugger.py"]
    output = run_command(command)
    print(f"     ✅  Отчёт диагностики обновлён...\n     ✅  Отчёт сохранён в {DEBUG_REPORT_PATH}")


def generate_test_report():
    """Запускает тестирование проекта для создания test_report.txt."""
    print("\n")  # Добавлена строка перед генерацией
    animate_message("🤖  Генерация тестового отчёта")
    command = [sys.executable, PROJECT_ROOT / "modules" / "test_report_generator.py"]
    output = run_command(command)
    print(f"     ✅  Тестовый отчёт обновлён...\n     ✅  Отчёт сохранён в {TEST_REPORT_PATH}")


def parse_reports(debug_report_path, test_report_path, messages_db_path):
    """Парсер для анализа отчетов."""
    with open(messages_db_path, "r", encoding="utf-8") as db_file:
        messages_db = json.load(db_file)
    
    findings = []

    # Анализ debug_report
    with open(debug_report_path, "r", encoding="utf-8") as debug_file:
        debug_report = debug_file.read()
        if "firewall-cmd --add-port" in debug_report:
            findings.append(messages_db["firewall_issue"])
    
    # Анализ test_report
    with open(test_report_path, "r", encoding="utf-8") as test_file:
        test_report = test_file.read()
        if "Gradio: ❌" in test_report:
            findings.append(messages_db["gradio_not_running"])
        if "Missing" in test_report:
            findings.append(messages_db["missing_files"])
    
    return findings


def get_paths_from_settings():
    """Собирает пути из settings.py."""
    from settings import (
        BASE_DIR, PROJECT_DIR, WG_CONFIG_DIR, QR_CODE_DIR,
        USER_DB_PATH, DEBUG_REPORT_PATH, TEST_REPORT_PATH
    )
    return {
        "BASE_DIR": BASE_DIR,
        "PROJECT_DIR": PROJECT_DIR,
        "WG_CONFIG_DIR": WG_CONFIG_DIR,
        "QR_CODE_DIR": QR_CODE_DIR,
        "USER_DB_PATH": USER_DB_PATH,
        "DEBUG_REPORT_PATH": DEBUG_REPORT_PATH,
        "TEST_REPORT_PATH": TEST_REPORT_PATH
    }


def format_message(message, paths):
    """Форматирует сообщение, заменяя переменные путями из settings.py."""
    for key, path in paths.items():
        message = message.replace(f"{{{key}}}", str(path))
    return message


def display_message_slowly(title, message, paths):
    """Красивый вывод сообщения с форматированием."""
    formatted_message = format_message(message, paths)
    print(f"\n       {title}\n       {'=' * (len(title) + 2)}\n")  # Исправлены полоски "=="
    for line in formatted_message.split("\n"):
        if not line.strip():
            print("       ")
            continue
        print("       ", end="")
        for char in line:
            print(char, end="", flush=True)
            time.sleep(0.01)  # Уменьшено время на вывод символов
        print()
        time.sleep(0.05)  # Уменьшено время между строками


def main():
    """Основной запуск программы."""
    generate_debug_report()
    generate_test_report()
    print(f"\n   🎉  Завершаю анализ, пожалуйста подождите 🤖")
    print(f"   🎯  Вот что мы обнаружили:\n")  # Исправлен отступ на один уровень вниз

    # Запуск анализа
    paths = get_paths_from_settings()
    findings = parse_reports(DEBUG_REPORT_PATH, TEST_REPORT_PATH, MESSAGES_DB_PATH)
    if findings:
        for finding in findings:
            display_message_slowly(finding["title"], finding["message"], paths)
    else:
        print("\n       ✅  Всё выглядит хорошо! Проблем не обнаружено.")
    print("\n")


if __name__ == "__main__":
    main()
