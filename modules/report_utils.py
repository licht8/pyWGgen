#!/usr/bin/env python3
# modules/report_utils.py
# ===========================================
# Модуль для работы с отчетами проекта wg_qr_generator
# ===========================================
# Этот модуль предоставляет функции для генерации и отображения отчетов,
# включая полный отчет, краткий отчет и обобщенный отчет о состоянии проекта.
#
# Пример использования:
# ---------------------
# from modules.report_utils import generate_project_report, display_test_report, display_summary_report
#
# generate_project_report()
# display_test_report()
# display_summary_report()
#
# Версия: 1.2
# Обновлено: 2024-12-02

from settings import SUMMARY_REPORT_PATH, TEST_REPORT_PATH
from modules.test_report_generator import generate_report


def generate_project_report():
    """Генерация полного отчета."""
    print("\n  📋  Запуск генерации полного отчета...")
    generate_report()


def display_test_report():
    """Вывод содержимого полного отчета в консоль."""
    if TEST_REPORT_PATH.exists():
        with open(TEST_REPORT_PATH, "r", encoding="utf-8") as file:
            print(file.read())
    else:
        print(f"  ❌  Файл полного отчета не найден: {TEST_REPORT_PATH}")


def display_test_summary():
    """Вывод краткого отчета."""
    if TEST_REPORT_PATH.exists():
        with open(TEST_REPORT_PATH, "r", encoding="utf-8") as file:
            lines = file.readlines()
            summary_keys = [
                "Дата и время",
                "WireGuard статус",
                "Gradio",
                "Открытые порты",
                "wg0.conf"
            ]
            print("\n=== Краткий отчет о состоянии проекта ===")
            for line in lines:
                if any(key in line for key in summary_keys):
                    print(line.strip())
            print("\n=========================================\n")
    else:
        print(f"  ❌  Файл полного отчета не найден: {TEST_REPORT_PATH}")


def display_summary_report():
    """
    Читает и выводит содержимое обобщенного отчета.
    Использует путь к файлу из settings.py.
    """
    try:
        if not SUMMARY_REPORT_PATH.exists():
            print(f" ❌ Файл обобщенного отчета не найден: {SUMMARY_REPORT_PATH}")
            return

        with open(SUMMARY_REPORT_PATH, "r", encoding="utf-8") as file:
            content = file.read()

        #print("\n=== 📋 Обобщенный отчет о состоянии проекта ===\n")
        print(content)

    except Exception as e:
        print(f" ❌ Ошибка при чтении обобщенного отчета: {e}")


# Пример использования
if __name__ == "__main__":
    print("=== Тестирование функций работы с отчетами ===\n")
    display_summary_report()
