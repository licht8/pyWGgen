#!/usr/bin/env python3
# ai_assistant/scripts/wg_data_analyzer.py
# ==================================================
# Скрипт для сбора и анализа данных WireGuard.
# Версия: 1.3 (2024-12-21)
# ==================================================
# Описание:
# Этот скрипт собирает данные из трёх источников:
# - Команда `sudo wg show` (текущее состояние WireGuard);
# - Файл конфигурации `/etc/wireguard/wg0.conf`;
# - Файл параметров `/etc/wireguard/params`.
# 
# Данные анализируются и сохраняются в формате JSON для дальнейшего
# использования, включая передачу в LLM для обработки.
# 
# Скрипт может работать как модуль (вызов функций) или как самостоятельный файл.
# ==================================================

import subprocess
import json
import os
import sys
import requests
from pathlib import Path

# Убедимся, что путь к settings.py доступен
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Попытка импортировать настройки проекта
try:
    from settings import BASE_DIR, SERVER_CONFIG_FILE, PARAMS_FILE
except ModuleNotFoundError as e:
    raise ImportError("Не удалось найти модуль settings. Убедитесь, что файл settings.py находится в корне проекта.") from e

def get_wg_status():
    """Получает состояние WireGuard через команду `wg show`."""
    try:
        output = subprocess.check_output(["sudo", "wg", "show"], text=True)
        return output
    except subprocess.CalledProcessError as e:
        return f"Error executing wg show: {e}"

def read_config_file(filepath):
    """Читает содержимое конфигурационного файла."""
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file {filepath}: {e}"

def parse_wg_show(output):
    """Парсит вывод команды `wg show` и извлекает данные о пирах."""
    peers = []
    for line in output.splitlines():
        if line.startswith("peer:"):
            peers.append(line.split(":")[1].strip())
    return {"peers": peers}

def parse_config_file(content):
    """Парсит содержимое конфигурационного файла."""
    config = {}
    for line in content.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()
    return config

def collect_and_analyze_wg_data():
    """Собирает данные из источников и возвращает их в виде словаря."""
    data = {}

    # Сбор данных
    wg_status = get_wg_status()
    wg0_config = read_config_file(SERVER_CONFIG_FILE)
    params_config = read_config_file(PARAMS_FILE)

    # Анализ данных
    data["wg_status"] = parse_wg_show(wg_status) if "Error" not in wg_status else wg_status
    data["wg0_config"] = parse_config_file(wg0_config) if "Error" not in wg0_config else wg0_config
    data["params_config"] = parse_config_file(params_config) if "Error" not in params_config else params_config

    return data

def save_to_json(data, output_file):
    """Сохраняет данные в формате JSON в указанный файл."""
    try:
        with open(output_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")

def query_llm(prompt, api_url="http://10.67.67.2:11434/api/generate", max_tokens=500):
    """Отправляет запрос в LLM и возвращает ответ."""
    try:
        response = requests.post(api_url, json={"prompt": prompt, "max_tokens": max_tokens})
        response.raise_for_status()
        return response.json().get("generated_text", "No response")
    except requests.RequestException as e:
        return f"Error querying LLM: {e}"

def generate_prompt(wg_data):
    """Создает системный промпт для анализа данных."""
    return f"""
    Вы профессиональный администратор WireGuard. Вот данные о текущем состоянии сервера:

    WG Show Status:
    {json.dumps(wg_data['wg_status'], indent=4)}

    WG0 Config:
    {json.dumps(wg_data['wg0_config'], indent=4)}

    Params Config:
    {json.dumps(wg_data['params_config'], indent=4)}

    Проведите анализ данных, выявите возможные проблемы и дайте полезные рекомендации. Включите команды для их решения.
    """

if __name__ == "__main__":
    output_path = BASE_DIR / "ai_assistant/inputs/wg_analysis.json"
    data = collect_and_analyze_wg_data()
    save_to_json(data, output_path)

    # Генерация промпта и запрос к LLM
    prompt = generate_prompt(data)
    llm_response = query_llm(prompt)

    print("LLM Analysis Output:")
    print(llm_response)
