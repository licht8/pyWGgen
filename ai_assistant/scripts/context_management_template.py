#!/usr/bin/env python3
# ai_assistant/scripts/chat_with_context.py
# ==================================================
# Скрипт для взаимодействия с LLM-моделью с учетом
# сохранения контекста диалога.
# Версия: 1.4
# ==================================================

import requests
import sys
from pathlib import Path
from datetime import datetime
import logging
import readline  # Для поддержки навигации и редактирования в консоли

# === Настройка путей ===
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
HISTORY_FILE = BASE_DIR / "ai_assistant/context/context_history.txt"
MAX_HISTORY_LENGTH = 50  # Максимальное количество сообщений в истории

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(BASE_DIR / f'logs/chat_with_context_{datetime.now().strftime("%Y%m%d")}.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.propagate = False

# === Глобальная переменная для хранения истории ===
dialog_history = []

# === Функции ===
def save_dialog_history():
    """Сохраняет историю диалога в текстовый файл."""
    try:
        with open(HISTORY_FILE, "w") as file:
            file.write("\n".join(dialog_history))
        logger.info(f"История диалога сохранена в {HISTORY_FILE}")
    except Exception as e:
        logger.error(f"Ошибка сохранения истории диалога: {e}")

def load_dialog_history():
    """Загружает историю диалога из текстового файла."""
    global dialog_history
    if HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0:
        try:
            with open(HISTORY_FILE, "r") as file:
                dialog_history = file.read().splitlines()
            logger.info(f"История диалога загружена из {HISTORY_FILE}")
        except Exception as e:
            logger.error(f"Ошибка загрузки истории диалога: {e}")
            dialog_history = []
    else:
        dialog_history = []

def query_llm_with_context(user_input):
    """Отправляет запрос в LLM с учетом истории диалога."""
    global dialog_history

    # Добавляем сообщение пользователя в историю
    dialog_history.append(f"Вы: {user_input}")
    if len(dialog_history) > MAX_HISTORY_LENGTH * 2:  # Умножаем на 2 (по одному сообщению от пользователя и ассистента)
        dialog_history = dialog_history[-MAX_HISTORY_LENGTH * 2:]

    payload = {
        "model": MODEL,
        "prompt": "\n".join(dialog_history),
        "stream": False
    }

    try:
        response = requests.post(LLM_API_URL, json=payload)
        response.raise_for_status()

        # Получаем ответ от модели
        model_response = response.json().get("response", "<Нет ответа>")
        dialog_history.append(f"Ассистент: {model_response}")

        # Сохраняем историю
        save_dialog_history()

        return model_response
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к модели: {e}")
        return None

# === Основной процесс ===
if __name__ == "__main__":
    load_dialog_history()

    print("Добро пожаловать в чат с LLM! Введите 'выход' для завершения.")

    try:
        while True:
            user_input = input("Вы: ")
            if user_input.lower() == "выход":
                print("Чат завершен. История сохранена.")
                break

            response = query_llm_with_context(user_input)
            if response:
                print(f"Ассистент: {response}")
            else:
                print("Ошибка: ответ от модели отсутствует.")
    except KeyboardInterrupt:
        print("\nЧат прерван пользователем. История сохранена.")
        save_dialog_history()
        sys.exit(0)
