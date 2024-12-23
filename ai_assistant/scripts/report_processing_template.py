#!/usr/bin/env python3
# report_processing_template.py
# ==================================================
# Скрипт для обработки данных и отправки запросов в LLM-модель.
# Версия: 1.1
# ==================================================

import sys
import requests
import logging
from pathlib import Path
from datetime import datetime

# === Настройка путей ===
# Добавляем корневую директорию проекта в sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Импорт настроек проекта
try:
    from settings import BASE_DIR, LLM_API_URL
except ImportError as e:
    print(f"Ошибка импорта settings: {e}")
    sys.exit(1)

# === Настройки ===
MODEL = "qwen2:7b"  # Имя модели для обработки
PROMPT_POSITION = "before"  # Расположение системного промпта: "before" или "after"

# Пути к файлам
DATA_FILE = BASE_DIR / "ai_assistant/inputs/test_data.txt"  # Путь к файлу с данными
PROMPT_FILE = BASE_DIR / "ai_assistant/prompts/test_prompt.txt"  # Путь к файлу с промптом

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(BASE_DIR / f'logs/report_processing_{datetime.now().strftime("%Y%m%d")}.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.propagate = False

# === Функции ===
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

def process_report():
    """Обрабатывает данные и отправляет запрос в LLM."""
    logger.info("\n=== Запуск обработки отчетов ===")

    # Чтение данных и промпта
    data = read_file(DATA_FILE)
    prompt = read_file(PROMPT_FILE)

    # Формирование данных для отправки
    if PROMPT_POSITION == "before":
        combined_data = f"{prompt}\n\n{data}"
    else:
        combined_data = f"{data}\n\n{prompt}"

    logger.info("Отправка данных в LLM...")
    response = query_llm(LLM_API_URL, combined_data, MODEL)

    if response:
        logger.info(f"Ответ от LLM:\n{response}")
    else:
        logger.error("Ответ от LLM отсутствует.")

# === Точка входа ===
if __name__ == "__main__":
    process_report()
