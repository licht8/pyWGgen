#!/usr/bin/env python3
# modules/report_utils.py
# Модуль для работы с отчетами

import os
from modules.test_report_generator import generate_report

TEST_REPORT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_report.txt"))

def generate_project_report():
    """Генерация полного отчета."""
    print("\n  📋  Запуск генерации отчета...")
    generate_report()

def display_test_report():
    """Вывод содержимого полного отчета в консоль."""
    if os.path.exists(TEST_REPORT_FILE):
        with open(TEST_REPORT_FILE, "r") as file:
            print(file.read())
    else:
        print(f"  ❌  Файл отчета {TEST_REPORT_FILE} не найден.")

def display_test_summary():
    """Вывод краткого отчета."""
    if os.path.exists(TEST_REPORT_FILE):
        with open(TEST_REPORT_FILE, "r") as file:
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
        print(f"  ❌  Файл отчета {TEST_REPORT_FILE} не найден.")
