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
    """Красивый вывод сообщения с отступами и постепенным отображением текста."""
    # Отображение заголовка
    print(f"\n  {title}\n  {'=' * len(title)}\n")  # Отступы перед заголовком

    # Отладочная информация
    print("\n[DEBUG] Начало обработки сообщения\n")
    print(f"[DEBUG] Исходный текст:\n{message}\n")

    # Обработка каждой строки сообщения
    for line in message.split("\n"):
        # Отладка для каждой строки
        print(f"[DEBUG] Обработка строки: {repr(line)}")
        
        # Если строка пустая, просто переносим
        if not line.strip():
            print("  [DEBUG] Пустая строка")
            print("  ")  # Пустая строка с отступом
            continue
        
        # Постепенный вывод строки с отступами
        print("  ", end="")  # Отступ перед строкой
        for word in line.split():
            print(word, end=" ", flush=True)
            time.sleep(0.05)  # Задержка между словами
        print()  # Завершаем строку после вывода всех слов
        time.sleep(0.1)  # Небольшая пауза между строками

    print("\n[DEBUG] Конец обработки сообщения\n")

def main():
    """Основной запуск программы."""
    findings = parse_reports(DEBUG_REPORT_PATH, TEST_REPORT_PATH, MESSAGES_DB_PATH)
    if findings:
        print("\n🎉  Анализ завершён. Вот что мы обнаружили:\n")
        for finding in findings:
            display_message_slowly(finding["title"], finding["message"])
    else:
        print("\n✅  Всё выглядит хорошо! Проблем не обнаружено.\n")

if __name__ == "__main__":
    main()
