import json
import time
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Импорт настроек
from settings import DEBUG_REPORT_PATH, TEST_REPORT_PATH, MESSAGES_DB_PATH

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
    """Красивый вывод сообщения с отступами и сохранением всех пробелов."""
    # Убираем лишние пробелы у заголовка для подсчёта длины
    clean_title = title.strip()

    # Определяем длину заголовка без учёта пробелов
    title_length = len(clean_title) + 1  # Увеличиваем длину разделителя на 1

    # Отображение заголовка с корректно выровненным разделителем
    print(f"\n  {clean_title}")  # Выводим заголовок с отступом
    print(f"  {'=' * title_length}\n")  # Разделитель на 1 символ длиннее

    # Обработка каждой строки сообщения
    for line in message.split("\n"):
        if not line.strip():  # Пустая строка
            print("  ")  # Два пробела отступа
            continue

        # Постепенный вывод строки
        print("  ", end="")  # Отступ перед строкой
        for word in line:
            print(word, end="", flush=True)
            time.sleep(0.02)  # Задержка между символами
        print()  # Завершаем строку после вывода всех символов
        time.sleep(0.1)  # Небольшая пауза между строками

    # Добавляем пустую строку после сообщения
    print("\n")


def main():
    """Основной запуск программы."""
    findings = parse_reports(DEBUG_REPORT_PATH, TEST_REPORT_PATH, MESSAGES_DB_PATH)
    if findings:
        print("\n🎉  Анализ завершён. Вот что мы обнаружили:")
        for finding in findings:
            display_message_slowly(finding["title"], finding["message"])
    else:
        print("\n✅  Всё выглядит хорошо! Проблем не обнаружено.\n")

if __name__ == "__main__":
    main()
