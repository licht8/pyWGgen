#!/usr/bin/env python3
# ai_help/ai_help.py
# Скрипт для интерактивной справки проекта wg_qr_generator.
# Версия: 1.0
# Обновлено: 2024-11-29

import json
import sys
import time
from pathlib import Path

# Добавляем корневую директорию проекта
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Импортируем модули и настройки
from settings import HELP_JSON_PATH
from ai_diagnostics.modules.pause_rules import apply_pause, get_pause_rules

def display_message_slowly(message):
    """Имитация печати ИИ."""
    rules = get_pause_rules()  # Получаем правила пауз
    for line in message.split("\n"):
        if not line.strip():  # Пустая строка
            print("   ")
            apply_pause("\n", rules)
            continue

        print("   ", end="")
        for char in line:
            print(char, end="", flush=True)
            apply_pause(char, rules)
        print()  # Завершение строки
        time.sleep(0.05)


def load_help_data():
    """Загружает справочные данные из JSON файла."""
    try:
        with open(HELP_JSON_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Ошибка загрузки справочного файла: {e}")
        return {}


def display_help_menu(help_data):
    """Показывает меню разделов справки."""
    print("\n   📖  Справочная система")
    print("   ======================")
    for idx, (key, section) in enumerate(help_data.items(), start=1):
        print(f"   {idx}. {section['title']}")
        print(f"      {section['short']}\n")
    print("   0. Выйти из справки\n")


def display_detailed_help(section):
    """Показывает подробную информацию по разделу справки."""
    display_message_slowly(f"\n{section['title']}\n{'=' * (len(section['title']) + 2)}")
    display_message_slowly(section["detailed"])


def interactive_help():
    """Основная логика интерактивной справочной системы."""
    help_data = load_help_data()
    if not help_data:
        print("   ❌  Справочная информация недоступна.")
        return

    while True:
        display_help_menu(help_data)
        choice = input("   Выберите номер раздела или введите ключевое слово: ").strip().lower()

        if choice == "0" or choice in {"выход", "exit"}:
            print("   👋  До свидания!")
            break

        matched_sections = [
            section for section in help_data.values()
            if choice in section["id"] or choice in section["title"].lower()
        ]

        if len(matched_sections) == 1:
            display_detailed_help(matched_sections[0])
        elif len(matched_sections) > 1:
            print("   🔎  Найдено несколько совпадений:")
            for section in matched_sections:
                print(f"   - {section['title']}")
        else:
            print("   ❓  Ничего не найдено. Попробуйте снова.\n")


if __name__ == "__main__":
    interactive_help()
