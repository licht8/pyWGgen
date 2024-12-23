import subprocess
import sys
import requests
import logging
from pathlib import Path

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Параметры
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
sys.path.append(str(PROJECT_DIR))

try:
    from settings import BASE_DIR, LLM_API_URL
except ImportError as e:
    logger.error(f"Ошибка импорта settings: {e}")
    sys.exit(1)

# Пути
USER_PROMPT_FILE = BASE_DIR / "ai_assistant/prompts/generate_user_report.txt"
SYSTEM_PROMPT_FILE = BASE_DIR / "ai_assistant/prompts/generate_system_report.txt"
USER_REPORT_FILE = BASE_DIR / "ai_assistant/scripts/user_report.txt"
SYSTEM_REPORT_FILE = BASE_DIR / "ai_assistant/scripts/system_report.txt"

# Функции

def read_file(filepath):
    try:
        with open(filepath, "r") as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"Файл {filepath} не найден.")
        sys.exit(1)

def generate_report(script_name):
    try:
        subprocess.run(["python3", script_name], check=True, text=True)
        logger.info(f"{script_name} выполнен успешно.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при выполнении {script_name}: {e}")
        sys.exit(1)

def query_llm(api_url, data_to_send):
    payload = {
        "model": "qwen2:7b",
        "input": data_to_send,
        "max_tokens": 500,
        "temperature": 0.7
    }
    try:
        logger.info(f"Отправка запроса в LLM: {api_url}")
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        result = response.json().get("response", "<Пустой ответ от модели>")
        return result
    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к LLM: {e}")
        return "<Ошибка запроса к модели>"

def main():
    logger.info("Генерация отчетов...")

    # Генерация отчетов
    generate_report(BASE_DIR / "ai_assistant/scripts/generate_user_report.py")
    generate_report(BASE_DIR / "ai_assistant/scripts/generate_system_report.py")

    logger.info("\nЗагрузка отчетов и промптов...")

    # Проверочный запрос
    test_response = query_llm(LLM_API_URL, "Привет! Проверяем подключение к модели.")
    logger.info(f"Тестовый ответ от модели: {test_response}")
    if not test_response or "<Пустой ответ" in test_response:
        logger.error("Модель не отвечает корректно на тестовый запрос. Проверьте подключение.")
        sys.exit(1)

    # Запрос для пользовательского отчета
    user_report = read_file(USER_REPORT_FILE)
    user_prompt = read_file(USER_PROMPT_FILE)
    user_data_to_send = f"{user_prompt}\n\n{user_report}"
    logger.info("Отправка пользовательского отчета в LLM...")
    user_response = query_llm(LLM_API_URL, user_data_to_send)
    logger.info(f"Ответ от LLM для пользовательского отчета:\n{user_response}")

    # Запрос для системного отчета
    system_report = read_file(SYSTEM_REPORT_FILE)
    system_prompt = read_file(SYSTEM_PROMPT_FILE)
    system_data_to_send = f"{system_report}\n\n{system_prompt}"
    logger.info("Отправка системного отчета в LLM...")
    system_response = query_llm(LLM_API_URL, system_data_to_send)
    logger.info(f"Ответ от LLM для системного отчета:\n{system_response}")

if __name__ == "__main__":
    main()
