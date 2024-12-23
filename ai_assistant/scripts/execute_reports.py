#!/usr/bin/env python3
# ai_assistant/scripts/execute_reports.py
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

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Настройка путей
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
sys.path.append(str(PROJECT_DIR))

try:
    from settings import BASE_DIR, LLM_API_URL
except ImportError as e:
    logger.error(f"Ошибка импорта settings: {e}")
    sys.exit(1)

USER_PROMPT_FILE = BASE_DIR / "ai_assistant/prompts/generate_user_report.txt"
SYSTEM_PROMPT_FILE = BASE_DIR / "ai_assistant/prompts/generate_system_report.txt"
USER_REPORT_FILE = BASE_DIR / "ai_assistant/scripts/user_report.txt"
SYSTEM_REPORT_FILE = BASE_DIR / "ai_assistant/scripts/system_report.txt"

# Запрос к LLM
def query_llm(api_url, model, prompt):
    payload = {
        "model": model,
        "input": prompt,
        "stream": False
    }
    try:
        logger.info(f"Отправка запроса в LLM: {api_url}")
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        result = response.json().get("response", "<Пустой ответ от модели>")
        logger.info("Ответ получен.")
        return result
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к LLM: {e}")
        return f"Ошибка: {e}"

# Чтение файла
def read_file(filepath):
    try:
        with open(filepath, "r") as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"Файл {filepath} не найден.")
        sys.exit(1)

# Генерация отчета
def generate_report(script_path):
    try:
        subprocess.run(["python3", script_path], check=True, text=True)
        logger.info(f"{script_path} выполнен успешно.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при выполнении {script_path}: {e}")
        sys.exit(1)

# Основной процесс выполнения
def main():
    logger.info("Генерация отчетов...")

    # Генерация пользовательского отчета
    generate_report(BASE_DIR / "ai_assistant/scripts/generate_user_report.py")

    # Генерация системного отчета
    generate_report(BASE_DIR / "ai_assistant/scripts/generate_system_report.py")

    # Загрузка и отправка пользовательского отчета
    logger.info("Отправка пользовательского отчета в LLM...")
    user_report = read_file(USER_REPORT_FILE)
    user_prompt = read_file(USER_PROMPT_FILE)
    user_input = f"{user_prompt}\n\n{user_report}"
    user_response = query_llm(LLM_API_URL, "qwen2:7b", user_input)
    logger.info(f"Ответ от LLM для пользовательского отчета:\n{user_response}")

    # Загрузка и отправка системного отчета
    logger.info("Отправка системного отчета в LLM...")
    system_report = read_file(SYSTEM_REPORT_FILE)
    system_prompt = read_file(SYSTEM_PROMPT_FILE)
    system_input = f"{system_report}\n\n{system_prompt}"
    system_response = query_llm(LLM_API_URL, "qwen2:7b", system_input)
    logger.info(f"Ответ от LLM для системного отчета:\n{system_response}")

if __name__ == "__main__":
    main()
