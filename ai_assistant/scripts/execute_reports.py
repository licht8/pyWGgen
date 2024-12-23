#!/usr/bin/env python3
# execute_reports.py
# ==================================================
# Скрипт для выполнения последовательной генерации
# отчетов и запроса к LLM-модели.
# Версия: 1.3
# ==================================================

import subprocess
import sys
import requests
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
sys.path.append(str(PROJECT_DIR))

try:
    from settings import BASE_DIR, LLM_API_URL
except ImportError as e:
    print(f"Ошибка импорта settings: {e}")
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
        print(f"Файл {filepath} не найден.")
        sys.exit(1)

def generate_report(script_name):
    """Запускает скрипт для генерации отчета."""
    try:
        result = subprocess.run(["python3", script_name], check=True, text=True)
        print(f"{script_name} выполнен успешно.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении {script_name}: {e}")
        sys.exit(1)

def query_llm(api_url, report_file, prompt_file):
    """Выполняет запрос к LLM с отчетом и промптом."""
    report_data = read_file(report_file)
    prompt_data = read_file(prompt_file)

    # Добавляем промпт в нужное место
    if "user" in report_file.name:
        data_to_send = f"{prompt_data}\n\n{report_data}"
    else:
        data_to_send = f"{report_data}\n\n{prompt_data}"

    print(f"\nОтправка данных в LLM для {report_file}...")

    # Запрос к LLM API
    payload = {
        "model": "qwen2:7b",
        "input": data_to_send
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Проверяем на ошибки HTTP
        llm_response = response.json().get("output", "<Пустой ответ от модели>")
        print(f"Ответ от LLM для {report_file.name}:")
        print(llm_response)
    except requests.RequestException as e:
        print(f"Ошибка запроса к LLM для {report_file.name}: {e}")

def main():
    print("Генерация отчетов...")
    
    # Генерация отчетов
    generate_report(BASE_DIR / "ai_assistant/scripts/generate_user_report.py")
    generate_report(BASE_DIR / "ai_assistant/scripts/generate_system_report.py")

    print("\nЗагрузка отчетов и промптов...")

    # Запросы к LLM
    query_llm(LLM_API_URL, USER_REPORT_FILE, USER_PROMPT_FILE)
    query_llm(LLM_API_URL, SYSTEM_REPORT_FILE, SYSTEM_PROMPT_FILE)

if __name__ == "__main__":
    main()
