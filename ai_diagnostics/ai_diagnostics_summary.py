#!/usr/bin/env python3
# ai_diagnostics/ai_diagnostics_summary.py
# Скрипт для создания обобщенного отчета о состоянии проекта wg_qr_generator.
# Версия: 1.7
# Обновлено: 2024-12-02

import json
import subprocess
from pathlib import Path
import sys
import logging

# Добавляем корневую директорию проекта в sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))  # Добавляем корень проекта в sys.path

# Импортируем настройки
from settings import PROJECT_DIR, SUMMARY_REPORT_PATH, USER_DB_PATH, LOG_LEVEL

# Настройка логирования
logging.basicConfig(
    level=logging.getLevelName(LOG_LEVEL),  # Используем уровень из settings
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("diagnostics_summary.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def run_command(command):
    """Выполняет команду в терминале и возвращает результат."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при выполнении команды {command}: {e.stderr.strip()}")
        return f"Ошибка: {e.stderr.strip()}"


def check_ports():
    """Проверяет открытые порты."""
    command = ["ss", "-tuln"]
    result = run_command(command)
    open_ports = []
    if not result:
        logger.warning(f"Не удалось получить список открытых портов.")
        return open_ports

    for line in result.splitlines():
        if ":51820" in line:
            open_ports.append("51820 (WireGuard)")
        if ":7860" in line:
            open_ports.append("7860 (Gradio)")
    logger.debug(f"Открытые порты: {open_ports}")
    return open_ports


def check_firewall():
    """Проверяет состояние фаервола и список открытых портов."""
    command_status = ["firewall-cmd", "--state"]
    command_ports = ["firewall-cmd", "--list-ports"]
    status = run_command(command_status)
    if status != "running":
        logger.warning(f"Фаервол неактивен: {status}")
        return f"Фаервол: {status}", []
    open_ports = run_command(command_ports).split()
    logger.debug(f"Открытые порты фаервола: {open_ports}")
    return f"Фаервол: Активен", open_ports


def check_wireguard_status():
    """Проверяет, активен ли сервис WireGuard."""
    command_status = ["sudo", "systemctl", "is-active", "wg-quick@wg0"]
    command_info = ["sudo", "wg", "show"]
    status = run_command(command_status)
    logger.debug(f"WireGuard статус: {status}")

    if status == "active":
        wg_info = run_command(command_info)
        logger.debug(f"WireGuard информация:\n{wg_info}")
        return status, wg_info
    return status, "WireGuard неактивен"


def count_users():
    """Считает количество пользователей из user_records.json."""
    if USER_DB_PATH.exists():
        try:
            with open(USER_DB_PATH, "r", encoding="utf-8") as file:
                user_data = json.load(file)
                user_count = len(user_data)
                logger.debug(f"Обнаружено пользователей: {user_count}")
                return user_count, "user_records.json"
        except json.JSONDecodeError:
            logger.error(f"Ошибка чтения файла user_records.json.")
            return 0, "Ошибка чтения user_records.json"
    logger.warning(f"Файл user_records.json отсутствует.")
    return 0, "Отсутствует файл user_records.json"


def count_peers(wg_info):
    """Считает количество peer в выводе wg show."""
    if not wg_info:
        logger.warning(f"WireGuard информация недоступна.")
        return 0
    peer_count = sum(1 for line in wg_info.splitlines() if line.startswith("peer:"))
    logger.debug(f"Количество peer: {peer_count}")
    return peer_count


def generate_summary():
    """Создает обобщенный отчет."""
    logger.info(f"Начало генерации обобщенного отчета.")

    # Получение данных о пользователях
    total_users, user_source = count_users()

    # Проверка WireGuard
    wg_status, wg_info = check_wireguard_status()
    peers_count = count_peers(wg_info) if wg_status == "active" else 0

    # Проверка портов
    open_ports = check_ports()

    # Проверка фаервола
    firewall_status, firewall_ports = check_firewall()

    # Формируем отчет
    summary = [
        " === 📋 Обобщенный отчет о состоянии проекта ===",
        "\n 📂 Пользователи:",
        f"- Общее количество пользователей: {total_users} (Источник: {user_source})",
        "\n 🔒 WireGuard:",
        f" - Общее количество peer: {peers_count} (Источник: wg show)",
        f" - Статус WireGuard: {wg_status}",
        f" - Информация о WireGuard:\n{wg_info if wg_status == 'active' else ''}",
        "\n 🌐 Gradio:",
        f" - Статус: {'Не запущен' if '7860 (Gradio)' not in open_ports else 'Запущен'}",
        "   - Для запуска:",
        f"    1️⃣  Перейдите в директорию проекта: cd {PROJECT_DIR}",
        "    2️⃣  Выполните команду: python3 main.py",
        "\n 🔥 Фаервол:",
        f" - {firewall_status}",
        " - Открытые порты:",
        f"  - {', '.join(firewall_ports) if firewall_ports else 'Нет открытых портов'}",
        "\n 🎯 Рекомендации:",
        " - Убедитесь, что количество peer совпадает с количеством пользователей.",
        " - Если Gradio не запущен, выполните предложенные действия.",
        " - Проверьте, что порты для Gradio и WireGuard доступны через фаервол.\n\n"
    ]

    # Подстановка переменных
    formatted_summary = "\n".join(summary).format(
        PROJECT_DIR=PROJECT_DIR  # Добавил подстановку PROJECT_DIR
    )

    # Сохраняем отчет
    try:
        with open(SUMMARY_REPORT_PATH, "w", encoding="utf-8") as file:
            file.write(formatted_summary)
        logger.info(f"Обобщенный отчет сохранен: {SUMMARY_REPORT_PATH}")
        print(f"\n ✅ Обобщенный отчет сохранен:\n 📂 {SUMMARY_REPORT_PATH}")
    except IOError as e:
        logger.error(f"Ошибка записи обобщенного отчета: {e}\n")
        print(f" ❌ Ошибка сохранения отчета: {e}\n")


if __name__ == "__main__":
    generate_summary()
