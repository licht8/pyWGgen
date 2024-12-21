#!/usr/bin/env python3
# ai_assistant/scripts/wg_data_analyzer.py
# ==================================================
# Скрипт для сбора и анализа данных WireGuard.
# Версия: 2.5 (2024-12-21)
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
import uuid

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

file_handler = logging.FileHandler(BASE_DIR / "ai_assistant/logs/llm_interaction.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def get_last_restart():
    """Получает время последнего перезапуска WireGuard."""
    try:
        output = subprocess.check_output(["systemctl", "show", "wg-quick@wg0", "--property=ActiveEnterTimestamp"], text=True)
        if "ActiveEnterTimestamp=" in output:
            return output.split("ActiveEnterTimestamp=")[1].strip()
        else:
            return "No data"
    except Exception as e:
        logger.error(f"Error retrieving WireGuard restart time: {e}")
        return "No data"

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
    def convert_to_simple_format(size_str):
        """Конвертирует размер из строки в простой формат (MB или GB)."""
        try:
            size, unit = size_str.split()
            size = float(size)
            if unit.lower().startswith("kib"):
                size_mb = size / 1024
                return f"{size_mb:.2f} MB"
            elif unit.lower().startswith("mib"):
                return f"{size:.2f} MB"
            elif unit.lower().startswith("gib"):
                return f"{size:.2f} GB"
            else:
                return size_str
        except Exception:
            return "No data"

    peers = []
    current_peer = None

    for line in output.splitlines():
        line = line.strip()
        if line.startswith("peer:"):
            if current_peer:
                peers.append(current_peer)
            current_peer = {
                "PublicKey": line.split("peer:")[1].strip(),
                "Transfer": {"Received": "No data", "Sent": "No data"},
                "LatestHandshake": "No data"
            }
        elif "latest handshake:" in line and current_peer:
            handshake_data = line.split("latest handshake:")[1].strip()
            current_peer["LatestHandshake"] = handshake_data if handshake_data else "No data"
        elif "transfer:" in line and current_peer:
            transfer_data = line.split("transfer:")[1].split(",")
            if len(transfer_data) == 2:
                current_peer["Transfer"] = {
                    "Received": convert_to_simple_format(transfer_data[0].strip()) or "No data",
                    "Sent": convert_to_simple_format(transfer_data[1].strip()) or "No data"
                }

    if current_peer:
        peers.append(current_peer)

    return {"peers": peers}

    # Проверка на отсутствие данных и установка значений по умолчанию
    for peer in peers:
        peer["Transfer"]["Received"] = peer["Transfer"]["Received"] or "No data"
        peer["Transfer"]["Sent"] = peer["Transfer"]["Sent"] or "No data"
        peer["LatestHandshake"] = peer["LatestHandshake"] or "No data"

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
    data["last_restart"] = get_last_restart()

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
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "Ошибка: нет ответа")
    except requests.HTTPError as http_err:
        logger.error(f"HTTP ошибка при обращении к LLM: {http_err}")
        return f"HTTP Error: {http_err}"
    except Exception as e:
        logger.error(f"Ошибка при обращении к LLM: {e}")
        return f"Error: {e}"

def generate_prompt(system_prompt, wg_data):
    """Создает финальный промпт для анализа данных без дублирования."""
    report_id = str(uuid.uuid4())
    formatted_prompt = (
        f"{system_prompt}\n\n"
        f"Уникальный идентификатор отчета: {report_id}\n\n"
        f"**Состояние WireGuard:**\n"
    )

    for peer in wg_data['wg0_config']:
        formatted_prompt += (
            f"- Логин: {peer['login']}, PublicKey: {peer['peer'].get('PublicKey', 'Не найден')}\n"
        )

    formatted_prompt += (
        f"\n**Конфигурация:**\n"
        f"📊 Адрес: {wg_data['params_config'].get('SERVER_WG_IPV4', 'Не указан')}\n"
        f"📊 Порт: {wg_data['params_config'].get('SERVER_PORT', 'Не указан')}\n"
        f"📊 PublicKey: {wg_data['params_config'].get('SERVER_PUB_KEY', 'Не указан')}\n"
    )

    formatted_prompt += (
        f"\n**Параметры:**\n"
        f"📊 IP сервера: {wg_data['params_config'].get('SERVER_PUB_IP', 'Не указан')}\n"
        f"📊 DNS: {', '.join([wg_data['params_config'].get(f'CLIENT_DNS_{i}', '') for i in range(1, 5)])}\n"
    )

    formatted_prompt += (
        f"\n**Последний перезапуск:**\n"
        f"🕒 {wg_data.get('last_restart', 'Не указано')}\n"
    )

    formatted_prompt += (
        f"\n**Рекомендации:**\n"
        f"- 🔧 Проверьте статус пиров: `wg show`\n"
        f"- 🔧 Перезапустите WireGuard: `sudo systemctl restart wg-quick@wg0`\n"
        f"- 🔧 Проверьте доступность порта: `sudo ss -tuln | grep 51820`\n"
    )

    return formatted_prompt

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

    # Вывод результата
    print("\nLLM Analysis Output:")
    print(llm_response)
