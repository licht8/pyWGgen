#!/usr/bin/env python3
# ai_diagnostics/ai_diagnostics.py
# Скрипт для диагностики и анализа состояния проекта wg_qr_generator.
# Версия: 4.5
# Обновлено: 2024-12-02
# Исправлена обработка портов в выводе firewall-cmd.

import json
import time
import sys
import subprocess
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
    ANIMATION_SPEED,
    PRINT_SPEED,
    LINE_DELAY,
    GRADIO_PORT,
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

# Проверяемые порты
WIREGUARD_PORT = 51820
REQUIRED_PORTS = [f"{WIREGUARD_PORT}/udp", f"{GRADIO_PORT}/tcp"]

# Скрипты
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
    """Выводит анимированное сообщение с эффектом перемигивания."""
    for _ in range(3):
        for dots in range(1, 4):
            print(f"\r   {message}{'.' * dots}{' ' * (3 - dots)}", end="", flush=True)
            time.sleep(ANIMATION_SPEED)
    print(f"\r   {message} 🔎 ", flush=True)


def display_message_slowly(message):
    """Имитация печати ИИ."""
    for line in message.split("\n"):
        print("   ", end="")
        for char in line:
            print(char, end="", flush=True)
            time.sleep(PRINT_SPEED)
        print()
        time.sleep(LINE_DELAY)


def check_ports():
    """Проверяет состояние необходимых портов с выводом отладки."""
    command = ["sudo", "firewall-cmd", "--list-all"]
    result = run_command(command)
    logger.debug(f"Результат команды проверки фаервола:\n{result}")

    open_ports = []
    for line in result.splitlines():
        if "ports:" in line:
            logger.debug(f"Обрабатываем строку портов: {line.strip()}")
            ports_line = line.split("ports:")[1].strip()  # Извлекаем содержимое после 'ports:'
            open_ports = [port.strip() for port in ports_line.split()]  # Разделяем и очищаем список портов

    logger.debug(f"Обнаруженные открытые порты: {open_ports}")
    logger.debug(f"Требуемые порты для проверки: {REQUIRED_PORTS}")

    closed_ports = [port for port in REQUIRED_PORTS if port not in open_ports]
    return closed_ports


def execute_commands(commands):
    """Выполняет список команд и возвращает результат."""
    results = []
    for command in commands:
        logger.info(f"Выполняю команду: {command}")
        result = run_command(command.split())
        results.append(f"{command}:\n{result}")
    time.sleep(3)  # Небольшая задержка перед повторной проверкой
    return "\n".join(results)


def parse_reports(debug_report_path, test_report_path, messages_db_path):
    """Парсер для анализа отчетов."""
    try:
        with open(messages_db_path, "r", encoding="utf-8") as db_file:
            messages_db = json.load(db_file)
    except FileNotFoundError:
        logger.error(f" ❌ Файл messages_db.json не найден: {messages_db_path}")
        return [], []

    findings = []
    suggestions = []

    # Проверка портов
    closed_ports = check_ports()
    if closed_ports:
        findings.append(
            messages_db.get(
                "ports_closed",
                {"title": "🔒 Закрытые порты", "message": "Необходимые порты закрыты.", "commands": []},
            )
        )

    return findings, suggestions


def handle_findings(findings, paths):
    """Обрабатывает обнаруженные проблемы."""
    for finding in findings:
        title = finding["title"]
        message = format_message(finding["message"], paths)
        commands = finding.get("commands", [])

        display_message_slowly(f"\n   {title}\n   {'=' * (len(title) + 2)}\n")
        display_message_slowly(message)

        if commands:
            display_message_slowly("\n 🛠  Найдены команды для устранения проблемы. Попробовать выполнить их автоматически? (y/n): ")
            user_input = input().strip().lower()
            if user_input == "y":
                display_message_slowly(" ⚙️  Выполняю команды...")
                results = execute_commands(commands)
                display_message_slowly(f"\n 📝  Результат выполнения команд:\n{results}")
                display_message_slowly(" 🔄  Перезапускаю диагностику...")
                main()  # Повторный запуск диагностики
                return  # Завершаем текущую итерацию


def format_message(message, paths):
    """Форматирует сообщение, заменяя переменные путями."""
    for key, path in paths.items():
        message = message.replace(f"{{{key}}}", str(path))
    return message


def generate_summary_report():
    """Вызов генерации обобщенного отчета."""
    print("\n 🤖 Создание обобщенного отчета...")
    command = [sys.executable, str(SUMMARY_SCRIPT)]
    subprocess.run(command)


def main():
    """Основной запуск программы."""
    logger.info("Начало выполнения диагностики.")
    animate_message(" 🎉  Завершаю анализ, пожалуйста подождите 🤖")
    display_message_slowly("\n 🎯  Вот что мы обнаружили:")

    paths = {
        "DEBUG_REPORT_PATH": DEBUG_REPORT_PATH,
        "TEST_REPORT_PATH": TEST_REPORT_PATH,
        "PROJECT_DIR": PROJECT_DIR,
    }
    findings, _ = parse_reports(DEBUG_REPORT_PATH, TEST_REPORT_PATH, MESSAGES_DB_PATH)
    if findings:
        handle_findings(findings, paths)
    else:
        display_message_slowly(" ✅  Всё выглядит хорошо!\n 👍  Проблем не обнаружено.")

    print("\n")
    generate_summary_report()


if __name__ == "__main__":
    main()
