#!/usr/bin/env python3
# ai_help/ai_help.py
# Скрипт для интерактивной работы со справочной информацией.
# Версия: 1.0
# Обновлено: 2024-11-29

import json
import time
from pathlib import Path
from ai_diagnostics.modules.pause_rules import apply_pause, get_pause_rules
from ai_diagnostics.ai_diagnostics import display_message_slowly

# Пути
PROJECT_ROOT = Path(__file__).resolve().parent.parent
HELP_JSON_PATH = PROJECT_ROOT / "ai_help" / "ai_help.json"


def load_help_data():
    """Загружает справочные данные из JSON файла."""
    try:
        with open(HELP_JSON_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Ошибка загрузки файла справки: {e}")
        return {}


def display_menu(help_data):
    """Выводит меню выбора раздела."""
    print("\n   📚  Добро пожаловать в справочную систему\n")
    for key, section in help_data.items():
        display_message_slowly(f"   {section['id']} - {section['title']}")
    print("\n   🔎 Введите ключевое слово для поиска или ID раздела.\n   Нажмите Enter для выхода.\n")


def search_help(query, help_data):
    """Ищет разделы справки по запросу."""
    results = []
    for key, section in help_data.items():
        if query.lower() in section["title"].lower() or query.lower() in section["summary"].lower():
            results.append(section)
    return results


def display_section(section):
    """Выводит выбранный раздел справки."""
    display_message_slowly(f"\n   {section['title']}\n   {'=' * len(section['title'])}")
    display_message_slowly(f"\n   {section['summary']}\n")
    display_message_slowly("   Хотите узнать больше? (y/n)")
    choice = input("   > ").strip().lower()
    if choice == "y":
        display_message_slowly(f"\n   {section['content']}\n")
    else:
        display_message_slowly("\n   Возвращаемся в меню...\n")


def main():
    """Основная логика работы справочной системы."""
    help_data = load_help_data()
    if not help_data:
        print("Ошибка: данные справки не загружены.")
        return

    while True:
        display_menu(help_data)
        query = input("   Введите запрос: ").strip()

        if not query:
            print("\n   👋  Выход из справочной системы.\n")
            break

        results = search_help(query, help_data)
        if results:
            for section in results:
                display_section(section)
        else:
            display_message_slowly("\n   🔍  Ничего не найдено. Попробуйте снова.\n")


if __name__ == "__main__":
    main()
