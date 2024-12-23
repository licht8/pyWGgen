#!/usr/bin/env python3
# execute_reports.py
# ==================================================
# Скрипт для выполнения последовательной генерации
# отчетов и запроса к LLM-модели.
# Версия: 1.4
# ==================================================

import subprocess
import sys
import requests
from pathlib import Path
import logging
from datetime import datetime

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(f'execute_reports_{datetime.now().strftime("%Y%m%d")}.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.propagate = False

# Добавляем корневую директорию в PYTHONPATH
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
sys.path.append(str(PROJECT_DIR))

try:
    from settings import BASE_DIR, LLM_API_URL
except ImportError as e:
    logger.error(f"Ошибка импорта settings: {e}")
    sys.exit(1)

# Пути к отчетам и промптам
USER_PROMPT_FILE = BASE_DIR / "ai_assistant/prompts/generate_user_report.txt"
SYSTEM_PROMPT_FILE = BASE_DIR / "ai_assistant/prompts/generate_system_report.txt"
USER_REPORT_FILE = BASE_DIR / "ai_assistant/scripts/user_report.txt"
SYSTEM_REPORT_FILE = BASE_DIR / "ai_assistant/scripts/system_report.txt"

def read_file(filepath):
    """Читает содержимое файла."""
    try:
        with open(filepath, "r") as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"Файл {filepath} не найден.")
        sys.exit(1)

def generate_report(script_name):
    """Запускает скрипт для генерации отчета."""
    try:
        result = subprocess.run(["python3", script_name], check=True, text=True)
        logger.info(f"{script_name} выполнен успешно.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при выполнении {script_name}: {e}")
        sys.exit(1)

def query_llm(api_url, report_file, prompt_file, model="qwen2:7b"):
    """Выполняет запрос к LLM с отчетом и промптом."""
    report_data = read_file(report_file)
    prompt_data = read_file(prompt_file)

    # Формируем данные для отправки (промпт в конце данных для системного отчета)
    if "system" in report_file.name:
        combined_data = f"{report_data}\n\n{prompt_data}"
    else:
        combined_data = f"{prompt_data}\n\n{report_data}"

    data_to_send = {
        "model": model,
        "prompt": combined_data,
        "stream": False
    }

    logger.info(f"\nОтправка данных в LLM для {report_file}...")

    try:
        response = requests.post(api_url, json=data_to_send)
        response.raise_for_status()
        llm_response = response.json().get("response", "<Пустой ответ от модели>")
        logger.info(f"Ответ от LLM для {report_file.name}:\n{llm_response}")
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к LLM для {report_file.name}: {e}")


def main():
    logger.info("Генерация отчетов...")

    # Генерация отчетов
    generate_report(BASE_DIR / "ai_assistant/scripts/generate_user_report.py")
    generate_report(BASE_DIR / "ai_assistant/scripts/generate_system_report.py")

    logger.info("\nЗагрузка отчетов и промптов...")

    # Запросы к LLM
    query_llm(LLM_API_URL, USER_REPORT_FILE, USER_PROMPT_FILE)
    query_llm(LLM_API_URL, SYSTEM_REPORT_FILE, SYSTEM_PROMPT_FILE)

if __name__ == "__main__":
    main()
