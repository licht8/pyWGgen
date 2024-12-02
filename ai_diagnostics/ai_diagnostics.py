#!/usr/bin/env python3
# ai_diagnostics/ai_diagnostics.py
# Скрипт для диагностики и анализа состояния проекта wg_qr_generator.
# Версия: 3.9
# Обновлено: 2024-12-02
# Включает использование библиотеки logging для управления логами.

import json
import time
import sys
import subprocess
import random
import logging
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = PROJECT_ROOT / "modules"
DIAGNOSTICS_DIR = PROJECT_ROOT / "ai_diagnostics"

sys.path.append(str(PROJECT_ROOT))  # Добавляем путь к корню проекта
sys.path.append(str(MODULES_DIR))  # Добавляем путь к модулям

# Импорт из настроек
from settings import (
    DEBUG_REPORT_PATH,
    TEST_REPORT_PATH,
    MESSAGES_DB_PATH,
    PROJECT_DIR,
    LOG_LEVEL,
    LOG_FILE_PATH,
)

# Настраиваем logging
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Правильные пути для скриптов
DEBUGGER_SCRIPT = MODULES_DIR / "debugger.py"
TEST_REPORT_GENERATOR_SCRIPT = MODULES_DIR / "test_report_generator.py"
SUMMARY_SCRIPT = DIAGNOSTICS_DIR / "ai_diagnostics_summary.py"


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
    """Имитация печати ИИ."""
    for line in message.split("\n"):
        print("   ", end="")
        for char in line:
            print(char, end="", flush=True)
            time.sleep(0.03)
        print()
        time.sleep(0.1)


def generate_debug_report():
    """Запускает дебаггер для создания debug_report."""
    print("")
    animate_message(" 🤖  Генерация отчёта диагностики")
    command = [sys.executable, str(DEBUGGER_SCRIPT)]
    result = run_command(command)
    logger.debug(f"Ожидаемый путь к debug_report: {DEBUG_REPORT_PATH}")
    if not DEBUG_REPORT_PATH.exists():
        logger.warning(f"⚠️ Debug Report не был создан! Результат команды: {result}")
    else:
        logger.info(f"✅ Debug Report успешно создан.")


def generate_test_report():
    """Запускает тестирование проекта для создания test_report."""
    print("")
    animate_message(" 🤖  Генерация тестового отчёта")
    command = [sys.executable, str(TEST_REPORT_GENERATOR_SCRIPT)]
    result = run_command(command)
    logger.debug(f"Ожидаемый путь к test_report: {TEST_REPORT_PATH}")
    if not TEST_REPORT_PATH.exists():
        logger.warning(f"⚠️ Test Report не был создан! Результат команды: {result}")
    else:
        logger.info(f"✅ Test Report успешно создан.")


def parse_reports(debug_report_path, test_report_path, messages_db_path):
    """Парсер для анализа отчетов."""
    try:
        with open(messages_db_path, "r", encoding="utf-8") as db_file:
            messages_db = json.load(db_file)
    except FileNotFoundError:
        logger.error(f"❌ Файл messages_db.json не найден:\n 📂  {messages_db_path}")
        return []

    findings = []

    # Анализ debug_report
    if debug_report_path.exists():
        with open(debug_report_path, "r", encoding="utf-8") as debug_file:
            debug_report = debug_file.read()
            logger.debug(f"Содержимое Debug Report: {debug_report[:500]}...")  # Первые 500 символов
            if "firewall-cmd --add-port" in debug_report:
                findings.append(messages_db.get("firewall_issue", {"title": "Ошибка Firewall", "message": "Нет описания"}))
    else:
        logger.warning(f"⚠️ Debug Report отсутствует по пути: {debug_report_path}")

    # Анализ test_report
    if test_report_path.exists():
        with open(test_report_path, "r", encoding="utf-8") as test_file:
            test_report = test_file.read()
            logger.debug(f"Содержимое Test Report: {test_report[:500]}...")  # Первые 500 символов
            if "Gradio: ❌" in test_report:
                findings.append(messages_db.get("gradio_not_running", {"title": "Gradio Error", "message": "Нет описания"}))
            if "Missing" in test_report:
                findings.append(messages_db.get("missing_files", {"title": "Отсутствующие файлы", "message": "Нет описания"}))
            if "user_records.json: ❌" in test_report:
                findings.append(messages_db.get("missing_user_records", {"title": "Ошибка Users", "message": "Нет описания"}))
    else:
        logger.warning(f"⚠️ Test Report отсутствует по пути: {test_report_path}")

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


def generate_summary_report():
    """Вызов генерации обобщенного отчета."""
    print("\n 🤖 Создание обобщенного отчета...")
    command = [sys.executable, str(SUMMARY_SCRIPT)]
    subprocess.run(command)


def main():
    """Основной запуск программы."""
    logger.info("Начало выполнения диагностики.")

    generate_debug_report()
    generate_test_report()

    animate_message(" 🎉  Завершаю анализ, пожалуйста подождите 🤖 ")
    display_message_slowly(f"\n 🎯  Вот что мы обнаружили:")

    paths = {
        "DEBUG_REPORT_PATH": DEBUG_REPORT_PATH,
        "TEST_REPORT_PATH": TEST_REPORT_PATH,
        "PROJECT_DIR": PROJECT_DIR,
    }
    findings = parse_reports(DEBUG_REPORT_PATH, TEST_REPORT_PATH, MESSAGES_DB_PATH)
    if findings:
        for finding in findings:
            display_analysis_result(finding["title"], finding["message"], paths)
    else:
        display_message_slowly(" ✅  Всё выглядит хорошо! Проблем не обнаружено.")
    print("\n")

    # Генерация обобщенного отчета
    generate_summary_report()


if __name__ == "__main__":
    main()
