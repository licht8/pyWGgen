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
PROMPTS_DIR = BASE_DIR / "ai_assistant/prompts"
SCRIPTS_DIR = BASE_DIR / "ai_assistant/scripts"

USER_PROMPT_FILE = PROMPTS_DIR / "generate_user_report.txt"
SYSTEM_PROMPT_FILE = PROMPTS_DIR / "generate_system_report.txt"
USER_REPORT_FILE = SCRIPTS_DIR / "user_report.txt"
SYSTEM_REPORT_FILE = SCRIPTS_DIR / "system_report.txt"

def read_file(filepath):
    """Reads the content of a file."""
    try:
        with open(filepath, "r") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Файл {filepath} не найден.")
        sys.exit(1)

def generate_report(script_path):
    """Runs a script to generate a report."""
    try:
        result = subprocess.run(["python3", script_path], check=True, text=True)
        print(f"{script_path} выполнен успешно.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении {script_path}: {e}")
        sys.exit(1)

def query_llm(api_url, report_file, prompt_file):
    """Sends a request to the LLM with a report and prompt."""
    report_data = read_file(report_file)
    prompt_data = read_file(prompt_file)

    # Add prompt in the appropriate place
    if "user" in report_file.name:
        data_to_send = f"{prompt_data}\n\n{report_data}"
    else:
        data_to_send = f"{report_data}\n\n{prompt_data}"

    print(f"\nОтправка данных в LLM для {report_file}...")
    print(f"Данные, отправляемые в модель:\n{data_to_send}")


    # Send a request to the LLM API
    payload = {
        "model": "qwen2:7b",
        "input": data_to_send
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Check for HTTP errors
        llm_response = response.json().get("output", "<Пустой ответ от модели>")
        print(f"Ответ от LLM для {report_file.name}:")
        print(llm_response)
    except requests.RequestException as e:
        print(f"Ошибка запроса к LLM для {report_file.name}: {e}")

def main():
    print("Генерация отчетов...")
    
    # Generate reports
    generate_report(SCRIPTS_DIR / "generate_user_report.py")
    generate_report(SCRIPTS_DIR / "generate_system_report.py")

    print("\nЗагрузка отчетов и промптов...")

    # Queries to LLM
    query_llm(LLM_API_URL, USER_REPORT_FILE, USER_PROMPT_FILE)
    query_llm(LLM_API_URL, SYSTEM_REPORT_FILE, SYSTEM_PROMPT_FILE)

if __name__ == "__main__":
    main()
