#!/usr/bin/env python3
# ai_diagnostics/ai_help/ai_help.py
# Скрипт для работы со справочной системой проекта wg_qr_generator.
# Версия: 1.0
# Обновлено: 2024-11-29

import json
import time
from pathlib import Path
from settings import HELP_JSON_PATH
from ai_diagnostics.modules.pause_rules import apply_pause, get_pause_rules
from ai_diagnostics.ai_diagnostics import display_message_slowly


def load_help_data():
    """Загружает справочную информацию из JSON файла."""
    try:
        with open(HELP_JSON_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Ошибка загрузки справочного файла: {e}")
        return None


def display_help_menu(help_data):
    """Выводит главное меню справочной системы."""
    print("\n   📖  Справочная система")
    print("   ======================")
    for idx, key in enumerate(help_data, start=1):
        section = help_data[key]
        print(f"   {idx}. {section['title']}")
        print(f"      {section['short']}\n")
    print("   0. Выйти из справки")


def display_detailed_help(section):
    """Выводит подробную информацию о разделе."""
    print(f"\n   {section['title']}\n   {'=' * (len(section['title']) + 3)}")
    display_message_slowly(section["long"])


def search_help(query, help_data):
    """Ищет разделы справки по запросу."""
    query = query.lower()
    results = []
    for key, section in help_data.items():
        if query in section["title"].lower() or query in section["short"].lower() or query in section["long"].lower():
            results.append(section)
    return results


def handle_numeric_selection(selection, help_data):
    """Обрабатывает выбор пользователя через цифру."""
    try:
        selection = int(selection)
        keys = list(help_data.keys())
        if selection == 0:
            print("\n   📖  Выход из справочной системы.\n")
            return None
        elif 1 <= selection <= len(keys):
            section = help_data[keys[selection - 1]]
            display_detailed_help(section)
        else:
            print("\n   ❌  Неверный выбор. Попробуйте снова.")
    except ValueError:
        print("\n   ❌  Введите номер раздела.")
    return True


def interactive_help():
    """Интерактивное меню справочной системы."""
    help_data = load_help_data()
    if help_data is None:
        print("\n   ❌  Справочная информация недоступна.\n")
        return
    
    while True:
        display_help_menu(help_data)
        user_input = input("\n   Выберите номер раздела или введите ключевое слово: ").strip().lower()
        if user_input in {"q", "exit"}:
            print("\n   📖  Выход из справочной системы.\n")
            break
        elif user_input.isdigit():
            if handle_numeric_selection(user_input, help_data) is None:
                break
        else:
            matched_sections = search_help(user_input, help_data)
            if matched_sections:
                display_detailed_help(matched_sections[0])
            else:
                print("\n   ❌  Ничего не найдено. Попробуйте другой запрос.\n")


if __name__ == "__main__":
    interactive_help()
