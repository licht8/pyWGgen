import json
import time
import sys
from pathlib import Path

# Пути к файлам
DEBUG_REPORT_PATH = Path("debug_report.txt")  # Путь к отчету диагностики
TEST_REPORT_PATH = Path("test_report.txt")    # Путь к отчету тестирования
MESSAGES_DB_PATH = Path("messages_db.json")   # Путь к базе сообщений

def parse_reports(debug_report_path, test_report_path, messages_db_path):
    """Парсер для анализа отчетов."""
    with open(messages_db_path, "r", encoding="utf-8") as db_file:
        messages_db = json.load(db_file)
    
    findings = []

    # Анализ debug_report
    with open(debug_report_path, "r", encoding="utf-8") as debug_file:
        debug_report = debug_file.read()
        if "firewall-cmd --add-port" in debug_report:
            findings.append(messages_db["firewall_issue"])
    
    # Анализ test_report
    with open(test_report_path, "r", encoding="utf-8") as test_file:
        test_report = test_file.read()
        if "Gradio: ❌" in test_report:
            findings.append(messages_db["gradio_not_running"])
        if "Missing" in test_report:
            findings.append(messages_db["missing_files"])
    
    return findings

def display_message_slowly(title, message):
    """Постепенный вывод текста, имитирующий работу ИИ."""
    print(f"\n{title}\n{'=' * len(title)}\n")
    for word in message.split():
        print(word, end=" ", flush=True)
        time.sleep(0.1)  # Задержка между словами
    print("\n")

def main():
    """Основной запуск программы."""
    findings = parse_reports(DEBUG_REPORT_PATH, TEST_REPORT_PATH, MESSAGES_DB_PATH)
    if findings:
        print("🎉 Анализ завершён. Вот что мы обнаружили:\n")
        for finding in findings:
            display_message_slowly(finding["title"], finding["message"])
    else:
        print("✅ Всё выглядит хорошо! Проблем не обнаружено.")

if __name__ == "__main__":
    main()
