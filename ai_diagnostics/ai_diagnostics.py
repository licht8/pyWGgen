#!/usr/bin/env python3
# ai_diagnostics/ai_diagnostics.py
# Скрипт для диагностики и анализа состояния проекта wg_qr_generator.
# Версия: 3.6
# Обновлено: 2024-11-29
# Эта версия исправляет пути к модулям и файлам для генерации отчетов.

import json
import time
import sys
import subprocess
import random
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = PROJECT_ROOT / "modules"

sys.path.append(str(PROJECT_ROOT))  # Добавляем путь к корню проекта
sys.path.append(str(MODULES_DIR))  # Добавляем путь к модулям

# Импорт из настроек
from settings import DEBUG_REPORT_PATH, TEST_REPORT_PATH, MESSAGES_DB_PATH

# Правильные пути для скриптов и файлов
DEBUGGER_SCRIPT = MODULES_DIR / "debugger.py"
TEST_REPORT_GENERATOR_SCRIPT = MODULES_DIR / "test_report_generator.py"
DEBUG_LOG_PATH = Path("/root/pyWGgen/user/data/logs/diagnostics.log")


def run_command(command):
    """Запускает внешнюю команду и возвращает её результат."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Ошибка: {e.stderr.strip()}"


def debug_log(message):
    """Выводит сообщение для отладки."""
    print(f" 🛠️ [DEBUG] {message}")


def animate_message(message):
    """Выводит анимированное сообщение с эффектом перемигивания '...'. Время перемигивания до 2 секунд."""
    for _ in range(3):  # Три итерации перемигивания
        for dots in range(1, 4):
            print(f"\r   {message}{'.' * dots}{' ' * (3 - dots)}", end="", flush=True)
            time.sleep(random.uniform(0.2, 0.5))  # Задержка от 0.2 до 0.5 секунд
    print(f"\r   {message} 🤖", flush=True)  # Завершающее сообщение с иконкой


def display_message_slowly(message):
    """Имитация печати ИИ."""
    for line in message.split("\n"):
        print("   ", end="")
        for char in line:
            print(char, end="", flush=True)
            time.sleep(0.03)  # Пауза между символами
        print()  # Завершение строки
        time.sleep(0.1)  # Пауза между строками


def generate_debug_report():
    """Запускает дебаггер для создания свежего debug_report."""
    print("")
    animate_message(" 🤖  Генерация отчёта диагностики")
    command = [sys.executable, str(DEBUGGER_SCRIPT)]
    result = run_command(command)
    debug_log(f"Ожидаемый путь к debug_report: {DEBUG_LOG_PATH}")
    if not DEBUG_LOG_PATH.exists():
        debug_log(f" ⚠️ Debug Report не был создан! Результат команды: {result}")
    else:
        debug_log(" ✅ Debug Report успешно создан.")


def generate_test_report():
    """Запускает тестирование проекта для создания test_report.txt."""
    print("")
    animate_message(" 🤖  Генерация тестового отчёта")
    command = [sys.executable, str(TEST_REPORT_GENERATOR_SCRIPT)]
    result = run_command(command)
    debug_log(f"Ожидаемый путь к test_report: {TEST_REPORT_PATH}")
    if not TEST_REPORT_PATH.exists():
        debug_log(f" ⚠️ Test Report не был создан! Результат команды: {result}")
    else:
        debug_log(" ✅ Test Report успешно создан.")


def parse_reports(debug_report_path, test_report_path, messages_db_path):
    """Парсер для анализа отчетов."""
    with open(messages_db_path, "r", encoding="utf-8") as db_file:
        messages_db = json.load(db_file)
    
    findings = []

    # Анализ debug_report
    with open(debug_report_path, "r", encoding="utf-8") as debug_file:
        debug_report = debug_file.read()
        debug_log(f"Содержимое Debug Report: {debug_report[:500]}...")  # Первые 500 символов
        if "firewall-cmd --add-port" in debug_report:
            findings.append(messages_db["firewall_issue"])
    
    # Анализ test_report
    with open(test_report_path, "r", encoding="utf-8") as test_file:
        test_report = test_file.read()
        debug_log(f"Содержимое Test Report: {test_report[:500]}...")  # Первые 500 символов
        if "Gradio: ❌" in test_report:
            findings.append(messages_db["gradio_not_running"])
        if "Missing" in test_report:
            findings.append(messages_db["missing_files"])
        if "user_records.json: ❌" in test_report:
            findings.append(messages_db["missing_user_records"])
    
    return findings


def format_message(message, paths):
    """Форматирует сообщение, заменяя переменные путями."""
    for key, path in paths.items():
        message = message.replace(f"{{{key}}}", str(path))
    return message


def display_analysis_result(title, message, paths):
    """Красивый вывод результата анализа."""
    formatted_message = format_message(message, paths)
    display_message_slowly(f"\n   {title}\n   {'=' * (len(title) + 2)}\n")
    display_message_slowly(formatted_message)


def main():
    """Основной запуск программы."""
    debug_log("Начало выполнения диагностики.")

    generate_debug_report()
    generate_test_report()

    animate_message(" 🎉  Завершаю анализ, пожалуйста подождите 🤖")
    display_message_slowly(" 🎯  Вот что мы обнаружили:")

    # Запуск анализа
    findings = parse_reports(DEBUG_LOG_PATH, TEST_REPORT_PATH, MESSAGES_DB_PATH)
    if findings:
        for finding in findings:
            display_analysis_result(finding["title"], finding["message"], {})
    else:
        display_message_slowly(" ✅  Всё выглядит хорошо! Проблем не обнаружено.")
    print("\n")


if __name__ == "__main__":
    main()
