#!/usr/bin/env python3
# ai_diagnostics/ai_diagnostics.py
# Скрипт для диагностики и анализа состояния проекта wg_qr_generator.
# Генерирует отчёты и анализирует их, предоставляя рекомендации по исправлению проблем.
# Версия: 3.1
# Обновлено: 2024-11-29

import json
import time
import sys
import subprocess
import random
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AI_DIAGNOSTICS_DIR = PROJECT_ROOT / "ai_diagnostics"
MODULES_DIR = AI_DIAGNOSTICS_DIR / "modules"

sys.path.append(str(AI_DIAGNOSTICS_DIR))  # Добавляем ai_diagnostics
sys.path.append(str(MODULES_DIR))  # Добавляем ai_diagnostics/modules

# Импорт из настроек и модулей
from settings import DEBUG_REPORT_PATH, TEST_REPORT_PATH, MESSAGES_DB_PATH
from pause_rules import get_pause_rules, apply_pause


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


def display_message_slowly(message):
    """Имитация печати ИИ с учётом пауз."""
    rules = get_pause_rules()  # Получаем правила пауз
    for line in message.split("\n"):
        if not line.strip():  # Пустая строка
            print("   ")
            apply_pause("\n", rules)  # Пауза для новой строки
            continue

        print("   ", end="")
        for char in line:
            print(char, end="", flush=True)
            apply_pause(char, rules)  # Применяем паузу для символов
        print()  # Завершение строки
        time.sleep(0.05)  # Дополнительная пауза между строками


def generate_debug_report():
    """Запускает дебаггер для создания свежего debug_report.txt."""
    print("")
    animate_message("🤖  Генерация отчёта диагностики")
    command = [sys.executable, PROJECT_ROOT / "modules" / "debugger.py"]
    run_command(command)
    display_message_slowly(
        f"""
✅  Отчёт диагностики обновлён...
✅  Отчёт сохранён в:\n📂  {DEBUG_REPORT_PATH}
        """
    )


def generate_test_report():
    """Запускает тестирование проекта для создания test_report.txt."""
    print("")
    animate_message("🤖  Генерация тестового отчёта")
    command = [sys.executable, PROJECT_ROOT / "modules" / "test_report_generator.py"]
    run_command(command)
    display_message_slowly(
        f"""
✅  Тестовый отчёт обновлён...
✅  Отчёт сохранён в:\n📂  {TEST_REPORT_PATH}
        """
    )


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


def display_analysis_result(title, message, paths):
    """Красивый вывод результата анализа с имитацией ввода ИИ."""
    formatted_message = format_message(message, paths)
    display_message_slowly(f"\n   {title}\n   {'=' * (len(title) + 2)}\n")
    display_message_slowly(formatted_message)


def main():
    """Основной запуск программы."""
    generate_debug_report()
    generate_test_report()

    animate_message("🎉  Завершаю анализ, пожалуйста подождите 🤖")
    display_message_slowly("🎯  Вот что мы обнаружили:")

    # Запуск анализа
    paths = get_paths_from_settings()
    findings = parse_reports(DEBUG_REPORT_PATH, TEST_REPORT_PATH, MESSAGES_DB_PATH)
    if findings:
        for finding in findings:
            display_analysis_result(finding["title"], finding["message"], paths)
    else:
        display_message_slowly("✅  Всё выглядит хорошо! Проблем не обнаружено.")
    print("\n")


if __name__ == "__main__":
    main()
