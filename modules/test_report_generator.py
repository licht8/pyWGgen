#!/usr/bin/env python3
# modules/test_report_generator.py
# Генератор отчета о тестировании проекта wg_qr_generator

import os
from datetime import datetime

def generate_report():
    """Генерирует отчет о тестировании проекта."""
    report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../test_report.txt"))
    now = datetime.now().isoformat()

    report_content = f"""=== Отчет о тестировании wg_qr_generator ===
Дата и время: {now}

=== Проверка структуры проекта ===
"""

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    required_files = [
        "menu.py",
        "modules/__init__.py",
        "modules/project_status.py",
        "modules/manage_users_menu.py",
    ]

    for file in required_files:
        file_path = os.path.join(base_path, file)
        if os.path.exists(file_path):
            report_content += f"✅ Found: {file}\n"
        else:
            report_content += f"❌ Missing: {file}\n"

    with open(report_path, "w") as report_file:
        report_file.write(report_content)

    print(f"✅ Отчет сохранен в {report_path}")

if __name__ == "__main__":
    generate_report()
