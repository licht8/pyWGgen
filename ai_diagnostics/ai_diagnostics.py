#!/usr/bin/env python3
# ai_diagnostics/ai_diagnostics.py
# Скрипт для диагностики и анализа состояния проекта wg_qr_generator.
# Версия: 3.4
# Обновлено: 2024-11-29
# Добавлен отладочный вывод.

import json
import time
import sys
import subprocess
import random
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = PROJECT_ROOT / "ai_diagnostics" / "modules"

sys.path.append(str(PROJECT_ROOT))  # Добавляем путь к корню проекта
sys.path.append(str(MODULES_DIR))  # Добавляем путь к модулям

# Импорт из настроек и модулей
from settings import DEBUG_REPORT_PATH, TEST_REPORT_PATH, MESSAGES_DB_PATH
from pause_rules import get_pause_rules, apply_pause


def debug_log(message):
    """Выводит сообщение отладки."""
    print(f"🛠️ [DEBUG] {message}")


def run_command(command):
    """Запускает внешнюю команду и возвращает её результат."""
    try:
        debug_log(f"Выполняю команду: {' '.join(map(str, command))}")
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        debug_log(f"Результат команды: {result.stdout.strip()}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        debug_log(f"Ошибка выполнения команды: {e.stderr.strip()}")
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
            time.sleep(0.03)  # Увеличено время на вывод символа
            apply_pause(char, rules)  # Применяем паузу для знаков препинания
        print()  # Завершение строки
        time.sleep(0.1)  # Увеличена пауза между строками


def generate_debug_report():
    """Запускает дебаггер для создания свежего debug_report.txt."""
    print("")
    animate_message("🤖  Генерация отчёта диагностики")
    command = [sys.executable, PROJECT_ROOT / "ai_diagnostics" / "modules" / "debugger.py"]
    run_command(command)
    debug_log(f"Ожидаемый путь к debug_report: {DEBUG_REPORT_PATH}")
    if not DEBUG_REPORT_PATH.exists():
        debug_log("⚠️ Debug Report не был создан!")
    else:
        debug_log("✅ Debug Report успешно создан.")


def generate_test_report():
    """Запускает тестирование проекта для создания test_report.txt."""
    print("")
    animate_message("🤖  Генерация тестового отчёта")
    command = [sys.executable, PROJECT_ROOT / "ai_diagnostics" / "modules" / "test_report_generator.py"]
    run_command(command)
    debug_log(f"Ожидаемый путь к test_report: {TEST_REPORT_PATH}")
    if not TEST_REPORT_PATH.exists():
        debug_log("⚠️ Test Report не был создан!")
    else:
        debug_log("✅ Test Report успешно создан.")


def parse_reports(debug_report_path, test_report_path, messages_db_path):
    """Парсер для анализа отчетов."""
    debug_log(f"Чтение базы сообщений: {messages_db_path}")
    with open(messages_db_path, "r", encoding="utf-8") as db_file:
        messages_db = json.load(db_file)

    findings = []

    debug_log(f"Чтение debug_report: {debug_report_path}")
    if not debug_report_path.exists():
        debug_log("⚠️ Debug Report отсутствует!")
    else:
        with open(debug_report_path, "r", encoding="utf-8") as debug_file:
            debug_report = debug_file.read()
            debug_log(f"Содержимое Debug Report: {debug_report[:200]}...")  # Показываем первые 200 символов
            if "firewall-cmd --add-port" in debug_report:
                findings.append(messages_db["firewall_issue"])

    debug_log(f"Чтение test_report: {test_report_path}")
    if not test_report_path.exists():
        debug_log("⚠️ Test Report отсутствует!")
    else:
        with open(test_report_path, "r", encoding="utf-8") as test_file:
            test_report = test_file.read()
            debug_log(f"Содержимое Test Report: {test_report[:200]}...")  # Показываем первые 200 символов
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
    paths = {
        "BASE_DIR": BASE_DIR,
        "PROJECT_DIR": PROJECT_DIR,
        "WG_CONFIG_DIR": WG_CONFIG_DIR,
        "QR_CODE_DIR": QR_CODE_DIR,
        "USER_DB_PATH": USER_DB_PATH,
        "DEBUG_REPORT_PATH": DEBUG_REPORT_PATH,
        "TEST_REPORT_PATH": TEST_REPORT_PATH
    }
    debug_log(f"Загруженные пути из settings: {paths}")
    return paths


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
    debug_log("Начало выполнения диагностики.")
    generate_debug_report()
    generate_test_report()

    animate_message("🎉  Завершаю анализ, пожалуйста подождите 🤖")
    display_message_slowly("🎯  Вот что мы обнаружили:")

    # Запуск анализа
    paths = get_paths_from_settings()
    findings = parse_reports(DEBUG_REPORT_PATH, TEST_REPORT_PATH, MESSAGES_DB_PATH)
    if findings:
        debug_log(f"Обнаружено проблем: {len(findings)}")
        for finding in findings:
            display_analysis_result(finding["title"], finding["message"], paths)
    else:
        debug_log("✅ Проблемы не обнаружены.")
        display_message_slowly("✅  Всё выглядит хорошо! Проблем не обнаружено.")
    print("\n")


if __name__ == "__main__":
    main()
