#!/usr/bin/env python3
# ai_assistant/scripts/execute_reports.py
# ==================================================
# Скрипт для выполнения генерации отчетов и запроса к LLM модели.
# Версия: 1.0
# ==================================================

import subprocess
import requests
import os

# Параметры файлов
USER_REPORT_SCRIPT = "generate_user_report.py"
SYSTEM_REPORT_SCRIPT = "generate_system_report.py"
USER_REPORT_FILE = "user_report.txt"
SYSTEM_REPORT_FILE = "system_report.txt"
USER_PROMPT_FILE = "ai_assistant/prompts/generate_user_report.txt"
SYSTEM_PROMPT_FILE = "ai_assistant/prompts/generate_system_report.txt"

# URL для LLM модели (замените на реальный URL вашей модели)
LLM_API_URL = "http://localhost:8000/query"

def run_script(script_path):
    """Запускает указанный скрипт."""
    try:
        subprocess.run(["python3", script_path], check=True)
        print(f"{script_path} выполнен успешно.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении {script_path}: {e}")
        exit(1)

def load_file(filepath):
    """Загружает содержимое файла."""
    if not os.path.exists(filepath):
        print(f"Файл {filepath} не найден.")
        exit(1)
    with open(filepath, "r") as file:
        return file.read()

def query_llm(data, prompt, api_url=LLM_API_URL):
    """Отправляет запрос к LLM модели."""
    try:
        payload = {
            "model": "latest",  # Укажите модель, если нужно
            "prompt": f"{prompt}\n\n{data}",
            "max_tokens": 1500
        }
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "Нет ответа от модели.")
    except requests.RequestException as e:
        print(f"Ошибка при запросе к LLM модели: {e}")
        exit(1)

def main():
    # Шаг 1: Генерация отчетов
    print("Генерация отчетов...")
    run_script(USER_REPORT_SCRIPT)
    run_script(SYSTEM_REPORT_SCRIPT)

    # Шаг 2: Загрузка отчетов и промптов
    print("Загрузка отчетов и промптов...")
    user_report = load_file(USER_REPORT_FILE)
    system_report = load_file(SYSTEM_REPORT_FILE)
    user_prompt = load_file(USER_PROMPT_FILE)
    system_prompt = load_file(SYSTEM_PROMPT_FILE)

    # Шаг 3: Запрос к LLM для пользовательского отчета
    print("Запрос к LLM для пользовательского отчета...")
    user_result = query_llm(f"{user_prompt}\n\n{user_report}", user_prompt)
    print("\nРезультат для пользовательского отчета:\n")
    print(user_result)

    # Шаг 4: Запрос к LLM для системного отчета
    print("Запрос к LLM для системного отчета...")
    system_result = query_llm(f"{system_report}\n\n{system_prompt}", system_prompt)
    print("\nРезультат для системного отчета:\n")
    print(system_result)

if __name__ == "__main__":
    main()
