#!/usr/bin/env python3
# ai_assistant/scripts/execute_llm_reports.py
# ==================================================
# Скрипт для выполнения последовательной генерации
# отчетов и запроса к LLM-модели.
# Версия: 1.4
# ==================================================

import subprocess
import sys
import requests
import logging
from pathlib import Path
from datetime import datetime

# Добавление корневого пути проекта в sys.path для импорта settings
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = SCRIPT_DIR.parent.parent
    sys.path.append(str(PROJECT_ROOT))
    from settings import BASE_DIR, LLM_API_URL
except ImportError as e:
    print(f"Ошибка импорта settings: {e}")
    sys.exit(1)

# === Настройки ===

#MODEL = "qwen2:7b"  # Имя модели для обработки
MODEL = "gemma:7b"  # Имя модели для обработки
#MODEL = "dolphin-mixtral:latest"  # Имя модели для обработки
#MODEL = "qwen2:7b"  # Имя модели для обработки
USER_REPORT_SCRIPT = BASE_DIR / "ai_assistant/scripts/generate_user_report.py"
SYSTEM_REPORT_SCRIPT = BASE_DIR / "ai_assistant/scripts/generate_system_report.py"
USER_REPORT_FILE = BASE_DIR / "ai_assistant/outputs/user_report.txt"
SYSTEM_REPORT_FILE = BASE_DIR / "ai_assistant/outputs/system_report.txt"
USER_PROMPT_FILE = BASE_DIR / "ai_assistant/prompts/generate_user_report.txt"
SYSTEM_PROMPT_FILE = BASE_DIR / "ai_assistant/prompts/generate_system_report.txt"

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(BASE_DIR / f'logs/execute_reports_{datetime.now().strftime("%Y%m%d")}.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.propagate = False

# === Функции ===
def run_script(script_path):
    """Запускает указанный скрипт."""
    try:
        result = subprocess.run(["python3", script_path], check=True, text=True)
        logger.info(f"{script_path} выполнен успешно.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при выполнении {script_path}: {e}")
        sys.exit(1)

def read_file(filepath):
    """Читает содержимое файла."""
    try:
        with open(filepath, "r") as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"Файл {filepath} не найден.")
        sys.exit(1)

def query_llm(api_url, data, model):
    """Отправляет запрос в LLM и возвращает ответ."""
    payload = {
        "model": model,
        "prompt": data,
        "stream": False
    }
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "<Пустой ответ от модели>")
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к LLM: {e}")
        return None

def process_report(report_file, prompt_file, model):
    """Обрабатывает отчет и отправляет запрос в LLM."""
    report_data = read_file(report_file)
    prompt_data = read_file(prompt_file)

    # Системный промпт добавляется после данных
    combined_data = f"{report_data}\n\n{prompt_data}"

    logger.info(f"\nОтправка данных в LLM для {report_file}...")
    response = query_llm(LLM_API_URL, combined_data, model)

    if response:
        logger.info(f"Ответ от LLM для {report_file.name}:\n{response}")
    else:
        logger.error(f"Ответ от LLM для {report_file.name} отсутствует.")


# === Основной процесс ===
if __name__ == "__main__":
    logger.info("Генерация отчетов...")

    # Генерация пользовательского отчета
    run_script(USER_REPORT_SCRIPT)

    # Генерация системного отчета
    run_script(SYSTEM_REPORT_SCRIPT)

    logger.info("\nЗагрузка отчетов и промптов...")

    # Обработка пользовательского отчета
    process_report(USER_REPORT_FILE, USER_PROMPT_FILE, MODEL)

    # Обработка системного отчета
    #process_report(SYSTEM_REPORT_FILE, SYSTEM_PROMPT_FILE, MODEL)
    process_report(SYSTEM_PROMPT_FILE, SYSTEM_REPORT_FILE, MODEL)
