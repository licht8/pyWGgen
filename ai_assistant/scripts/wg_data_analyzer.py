#!/usr/bin/env python3
# ai_assistant/scripts/wg_data_analyzer.py
# ==================================================
# Скрипт для сбора и анализа данных WireGuard.
# Версия: 2.1 (2024-12-21)
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
import logging

# Убедимся, что путь к settings.py доступен
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:
    SCRIPT_DIR = Path.cwd()

PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Попытка импортировать настройки проекта
try:
    from settings import BASE_DIR, SERVER_CONFIG_FILE, PARAMS_FILE, LLM_API_URL
except ModuleNotFoundError as e:
    logger = logging.getLogger(__name__)
    logger.error("Не удалось найти модуль settings. Убедитесь, что файл settings.py находится в корне проекта.")
    print("Не удалось найти модуль settings. Убедитесь, что файл settings.py находится в корне проекта.")
    sys.exit(1)

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def get_wg_status():
    """Получает состояние WireGuard через команду `wg show`."""
    try:
        output = subprocess.check_output(["sudo", "wg", "show"], text=True)
        return output
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка выполнения команды wg show: {e}")
        return f"Error executing wg show: {e}"

def read_config_file(filepath):
    """Читает содержимое конфигурационного файла."""
    if not os.path.exists(filepath):
        logger.warning(f"Файл не найден: {filepath}")
        return f"File not found: {filepath}"
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Ошибка чтения файла {filepath}: {e}")
        return f"Error reading file {filepath}: {e}"

def parse_wg_show(output):
    """Парсит вывод команды `wg show` и извлекает данные о пирах."""
    peers = []
    for line in output.splitlines():
        if line.startswith("peer:"):
            peers.append(line.split(":")[1].strip())
    return {"peers": peers}

def parse_config_with_logins(content):
    """Парсит конфигурационный файл WireGuard и сопоставляет пиров с логинами."""
    peer_data = []
    current_login = None
    current_peer = {}

    for line in content.splitlines():
        line = line.strip()
        if line.startswith("### Client"):
            if current_peer:
                peer_data.append(current_peer)
            current_login = line.split("Client")[-1].strip()
            current_peer = {"login": current_login, "peer": {}}
        elif line.startswith("[Peer]"):
            if current_peer:
                peer_data.append(current_peer)
            current_peer = {"login": current_login, "peer": {}}
        elif "=" in line:
            key, value = map(str.strip, line.split("=", 1))
            if current_peer:
                current_peer["peer"][key] = value

    if current_peer:
        peer_data.append(current_peer)

    return peer_data

def parse_config_file(content):
    """Парсит содержимое конфигурационного файла и возвращает словарь."""
    config = {}
    for line in content.splitlines():
        if "=" in line:
            key, value = map(str.strip, line.split("=", 1))
            config[key] = value
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
    data["wg0_config"] = parse_config_with_logins(wg0_config) if "Error" not in wg0_config else wg0_config
    data["params_config"] = parse_config_file(params_config) if "Error" not in params_config else params_config

    return data

def save_to_json(data, output_file):
    """Сохраняет данные в формате JSON в указанный файл."""
    try:
        with open(output_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        logger.info(f"Данные сохранены в {output_file}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных в JSON: {e}")

def load_system_prompt(prompt_file):
    """Загружает системный промпт из файла."""
    try:
        with open(prompt_file, 'r') as file:
            prompt_data = json.load(file)
        return prompt_data.get("system_prompt", "")
    except Exception as e:
        logger.error(f"Ошибка загрузки системного промпта: {e}")
        return ""

def query_llm(prompt, api_url=LLM_API_URL, model="llama3:latest", max_tokens=500):
    """Отправляет запрос в LLM и возвращает ответ."""
    try:
        logger.info(f"Отправка запроса к LLM: {api_url}")
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        logger.debug(f"Payload: {json.dumps(payload, indent=4)}")
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        result = response.json()
        assistant_response = result.get("response", "Ошибка: нет ответа")
        logger.info(f"Ответ от LLM: {assistant_response}")
        return assistant_response
    except requests.HTTPError as http_err:
        logger.error(f"HTTP ошибка при обращении к LLM: {http_err} - {response.text}")
        return f"HTTP Error: {http_err}"
    except Exception as e:
        logger.error(f"Ошибка при обращении к LLM: {e}")
        return f"Error: {e}"

def generate_prompt(system_prompt, wg_data):
    """Создает финальный промпт для анализа данных."""
    return f"{system_prompt}\n\nWG Show Status:\n{json.dumps(wg_data['wg_status'], indent=4)}\n\nWG0 Config with Logins:\n{json.dumps(wg_data['wg0_config'], indent=4)}\n\nParams Config:\n{json.dumps(wg_data['params_config'], indent=4)}"

if __name__ == "__main__":
    output_path = BASE_DIR / "ai_assistant/inputs/wg_analysis.json"
    prompt_file = BASE_DIR / "ai_assistant/prompts/system_prompt.json"

    data = collect_and_analyze_wg_data()
    save_to_json(data, output_path)

    # Загрузка системного промпта
    system_prompt = load_system_prompt(prompt_file)
    prompt = generate_prompt(system_prompt, data)

    # Запрос к LLM
    llm_response = query_llm(prompt)

    print("LLM Analysis Output:")
    print(llm_response)
