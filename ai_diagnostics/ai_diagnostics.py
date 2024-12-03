#!/usr/bin/env python3
# ai_diagnostics/ai_diagnostics.py
# Скрипт для диагностики и анализа состояния проекта wg_qr_generator.
# Версия: 5.3
# Обновлено: 2024-12-02 22:00

import json
import time
import sys
import subprocess
import logging
from pathlib import Path

# Определяем пути проекта
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = PROJECT_ROOT / "modules"
DIAGNOSTICS_DIR = PROJECT_ROOT / "ai_diagnostics"
SETTINGS_PATH = PROJECT_ROOT / "settings.py"

# Добавляем пути в sys.path
sys.path.extend([str(PROJECT_ROOT), str(MODULES_DIR)])

# Проверяем наличие файла settings.py
if not SETTINGS_PATH.exists():
    raise FileNotFoundError(f"Файл настроек settings.py не найден по пути: {SETTINGS_PATH}")

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
    USER_DB_PATH,
    QR_CODE_DIR,
    WIREGUARD_PORT,
)

# Импорт функции для подсети WireGuard
from utils import get_wireguard_subnet

# Настраиваем logging
LOG_DIR = Path(LOG_FILE_PATH).parent
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.getLevelName(LOG_LEVEL),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Проверяемые порты
WIREGUARD_PORT = WIREGUARD_PORT
REQUIRED_PORTS = [f"{WIREGUARD_PORT}/udp", f"{GRADIO_PORT}/tcp"]

# Скрипты
SUMMARY_SCRIPT = DIAGNOSTICS_DIR / "ai_diagnostics_summary.py"

def check_gradio_status():
    """Проверяет, запущен ли Gradio на порту."""
    command = ["ss", "-tuln"]
    result = run_command(command)
    if not result:
        return False

    logger.debug(f"Результат команды проверки Gradio:\n{result}")

    for line in result.splitlines():
        if f":{GRADIO_PORT} " in line and "LISTEN" in line:
            return True
    return False

def execute_commands(commands):
    """Выполняет список команд и возвращает результат."""
    results = []
    for command in commands:
        logger.info(f"Выполняю команду: {command}")
        try:
            result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            results.append(f"{command}:\n{result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            results.append(f"{command}:\nОшибка: {e.stderr.strip()}")
    return "\n".join(results)


def run_command(command):
    """Запускает внешнюю команду и возвращает её результат."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при выполнении команды {' '.join(command)}: {e.stderr.strip()}")
        return None


def check_ports():
    """Проверяет состояние необходимых портов."""
    command = ["sudo", "firewall-cmd", "--list-all"]
    result = run_command(command)
    if not result:
        return []

    logger.debug(f"Результат проверки портов:\n{result}")
    open_ports = []
    for line in result.splitlines():
        if "ports:" in line:
            ports_line = line.split("ports:")[1].strip()
            open_ports.extend(ports_line.split())
    return [port for port in REQUIRED_PORTS if port not in open_ports]


def check_masquerade_rules():
    """Проверяет наличие правил маскарадинга для WireGuard."""
    command = ["sudo", "firewall-cmd", "--list-all"]
    result = run_command(command)
    if not result:
        return [{"type": "Ошибка", "rule": "Не удалось проверить маскарадинг"}]

    logger.debug(f"Результат проверки маскарадинга:\n{result}")
    try:
        wireguard_subnet = get_wireguard_subnet()
        required_rules = [
            {"type": "IPv4", "rule": f"{wireguard_subnet.split('/')[0].rsplit('.', 1)[0]}.0/24"},
            {"type": "IPv6", "rule": "fd42:42:42::0/24"}
        ]
    except Exception as e:
        logger.error(f"Ошибка при извлечении подсети WireGuard: {e}")
        return [{"type": "Ошибка", "rule": "Не удалось определить правила"}]

    missing_rules = []
    for rule in required_rules:
        rule_str = f'rule family="{rule["type"].lower()}" source address="{rule["rule"]}" masquerade'
        if rule_str not in result:
            missing_rules.append(rule)

    return missing_rules


def parse_reports(messages_db_path):
    """Парсер для анализа отчетов."""
    try:
        with open(messages_db_path, "r", encoding="utf-8") as db_file:
            messages_db = json.load(db_file)
    except FileNotFoundError:
        logger.error(f" ❌ Файл messages_db.json не найден: {messages_db_path}")
        return [], []

    findings, suggestions = [], []

    # Проверка закрытых портов
    closed_ports = check_ports()
    if closed_ports:
        report = messages_db.get("ports_closed", {})
        if report:
            report["message"] = report["message"].format(
                PROJECT_DIR=PROJECT_DIR,
                USER_DB_PATH=USER_DB_PATH,
                QR_CODE_DIR=QR_CODE_DIR
            )
            findings.append(report)

    # Проверка состояния маскарадинга
    missing_masquerade_rules = check_masquerade_rules()
    if missing_masquerade_rules:
        # Форматирование правил маскарадинга
        max_key_length = max(len(rule['type']) for rule in missing_masquerade_rules if isinstance(rule, dict))
        formatted_rules = "\n".join(
            f"        {rule['type']:<{max_key_length}}: {rule['rule']}" if isinstance(rule, dict) else f"        {rule}"
            for rule in missing_masquerade_rules
        )
        report = messages_db.get("masquerade_issue", {})
        if report:
            report["message"] = report["message"].format(
                MISSING_RULES=formatted_rules
            )
            findings.append(report)

    # Проверка состояния Gradio
    if not check_gradio_status():
        report = messages_db.get("gradio_not_running", {})
        if report:
            report["message"] = report["message"].format(
                PROJECT_DIR=PROJECT_DIR,
                GRADIO_PORT=GRADIO_PORT
            )
            suggestions.append(report)

    return findings, suggestions


def display_message_slowly(message, print_speed=None, end="\n", indent=True):
    """
    Построчный вывод сообщения с поддержкой отключения отступов и кастомной скорости печати.

    :param message: Сообщение для вывода.
    :param print_speed: Скорость вывода символов (в секундах). Если None, используется глобальная PRINT_SPEED.
    :param end: Символ завершения строки (по умолчанию "\n").
    :param indent: Если True, добавляет отступ в 3 пробела перед каждой строкой.
    """
    effective_speed = print_speed if print_speed is not None else PRINT_SPEED
    for line in message.split("\n"):
        if indent:
            print("   ", end="")  # Добавляем отступ только если indent=True
        for char in line:
            print(char, end="", flush=True)
            time.sleep(effective_speed)
        print(end, end="", flush=True)
        time.sleep(LINE_DELAY)




def handle_findings(findings):
    """Обрабатывает обнаруженные проблемы."""
    for finding in findings:
        # Отображаем заголовок и сообщение без полосок
        display_message_slowly(f"\n {finding['title']}\n{finding['message']}")
        
        # Проверяем наличие команд и предлагаем исправить
        commands = finding.get("commands", [])
        if commands:
            response = input(f"    🛠  Исправить автоматически? (y/n): ").strip().lower()
            if response in ["y", "д"]:
                display_message_slowly(f" ⚙️  Исправляю...\n")
                result = execute_commands(commands)
                display_message_slowly(f" 📝 Результат:\n    {result}")
            elif response in ["n", "н"]:
                display_message_slowly(f" 🚫 Пропускаю исправление.\n")
            else:
                display_message_slowly(f" ⚠️ Неверный ввод. Пропускаю исправление.\n")



def main():
    """Основной запуск программы."""
    logger.info("Начало диагностики")
    display_message_slowly("\n 🎯  Вот что мы обнаружили:")

    findings, suggestions = parse_reports(MESSAGES_DB_PATH)

    if findings:
        handle_findings(findings)

    if suggestions:
        for suggestion in suggestions:
            display_message_slowly(f"\n {suggestion['title']}\n {suggestion['message']}")

    if not findings and not suggestions:
        display_message_slowly(f" ✅  Всё хорошо!\n 👍  Проблем не обнаружено.\n")

    subprocess.run([sys.executable, str(SUMMARY_SCRIPT)])


if __name__ == "__main__":
    main()
