#!/usr/bin/env python3
# ai_assistant/scripts/context_handling_template.py
# ==================================================
# Шаблон скрипта для обработки данных и сохранения контекста.
# Версия: 1.2
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
CONTEXT_LIMIT = 10  # Максимальное количество сообщений для хранения контекста

# Пути к файлам
DATA_FILE = BASE_DIR / "ai_assistant/inputs/test_data.txt"  # Путь к файлу с данными
PROMPT_FILE = BASE_DIR / "ai_assistant/prompts/test_prompt.txt"  # Путь к файлу с промптом
CONTEXT_FILE = BASE_DIR / "ai_assistant/context/context_history.txt"  # Путь к файлу контекста

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(BASE_DIR / f'logs/context_handling_{datetime.now().strftime("%Y%m%d")}.log')
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

def update_context(context_file, new_data):
    """Обновляет файл контекста, добавляя новые данные."""
    context_dir = context_file.parent
    context_dir.mkdir(parents=True, exist_ok=True)  # Убедиться, что директория существует

    try:
        if not context_file.exists():
            context_file.touch()

        with open(context_file, "a+") as file:
            file.seek(0)
            lines = file.readlines()

            # Ограничиваем количество хранимых строк
            updated_lines = lines[-CONTEXT_LIMIT:] + [new_data + "\n"]
            file.seek(0)
            file.writelines(updated_lines)
            file.truncate()
    except Exception as e:
        logger.error(f"Ошибка обновления контекста в {context_file}: {e}")

def process_with_context():
    """Обрабатывает данные с использованием контекста и отправляет запрос в LLM."""
    logger.info("\n=== Запуск обработки с контекстом ===")

    # Чтение данных и промпта
    data = read_file(DATA_FILE)
    prompt = read_file(PROMPT_FILE)

    # Чтение текущего контекста
    context = ""
    if CONTEXT_FILE.exists():
        context = read_file(CONTEXT_FILE)

    # Формирование данных для отправки
    if PROMPT_POSITION == "before":
        combined_data = f"{prompt}\n\n{context}\n\n{data}"
    else:
        combined_data = f"{context}\n\n{data}\n\n{prompt}"

    logger.info("Отправка данных в LLM...")
    response = query_llm(LLM_API_URL, combined_data, MODEL)

    if response:
        logger.info(f"Ответ от LLM:\n{response}")
        update_context(CONTEXT_FILE, response)  # Сохранение ответа в контекст
    else:
        logger.error("Ответ от LLM отсутствует.")

# === Точка входа ===
if __name__ == "__main__":
    process_with_context()
