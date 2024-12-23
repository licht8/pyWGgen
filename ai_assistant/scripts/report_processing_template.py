#!/usr/bin/env python3
# ai_assistant/scripts/report_processing_template.py
# ==================================================
# Шаблон для обработки отчетов с использованием LLM.
# Версия: 1.0
# ==================================================

import requests
import sys
from pathlib import Path
import logging
from datetime import datetime

# === Настройки ===
MODEL = "qwen2:7b"  # Имя модели для обработки
PROMPT_POSITION = "after"  # Расположение системного промпта: "before" или "after"

DATA_FILE = "path/to/data.txt"  # Путь к файлу с данными
PROMPT_FILE = "path/to/prompt.txt"  # Путь к файлу с промптом
LLM_API_URL = "http://10.67.67.2:11434/api/generate"  # URL API модели

# === Настройка логирования ===
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(f'report_processing_{datetime.now().strftime("%Y%m%d")}.log')
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

def query_llm(api_url, model, data, prompt, prompt_position):
    """Выполняет запрос к LLM с данными и промптом."""
    if prompt_position == "before":
        combined_data = f"{prompt}\n\n{data}"
    else:
        combined_data = f"{data}\n\n{prompt}"

    payload = {
        "model": model,
        "prompt": combined_data,
        "stream": False
    }

    logger.info("\nОтправка данных в LLM...")

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        llm_response = response.json().get("response", "<Пустой ответ от модели>")
        logger.info(f"Ответ от LLM:\n{llm_response}")
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к LLM: {e}")
        sys.exit(1)

# === Основная логика ===
def main():
    logger.info("\n=== Запуск обработки отчетов ===")

    # Загрузка данных и промпта
    data = read_file(DATA_FILE)
    prompt = read_file(PROMPT_FILE)

    # Отправка данных в LLM
    query_llm(LLM_API_URL, MODEL, data, prompt, PROMPT_POSITION)

if __name__ == "__main__":
    main()
