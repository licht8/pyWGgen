#!/usr/bin/env python3
# ai_diagnostics/ai_help/ai_help.py
# Справочная система для проекта wg_qr_generator.
# Версия: 1.3
# Обновлено: 2024-11-29

import json
import sys
from pathlib import Path

# Добавляем пути к корню проекта и модулям
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODULES_DIR = PROJECT_ROOT / "ai_diagnostics" / "modules"

sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(MODULES_DIR))

# Импорты
from pause_rules import apply_pause, get_pause_rules
from ai_diagnostics.ai_diagnostics import display_message_slowly

HELP_JSON_PATH = PROJECT_ROOT / "ai_diagnostics" / "ai_help" / "ai_help.json"


def load_help_data():
    """Загружает справочные данные из JSON файла."""
    try:
        with open(HELP_JSON_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Ошибка загрузки справочного файла: {e}")
        return None


def save_help_section(section):
    """Сохраняет раздел справки в файл."""
    filename = f"{section['title'].strip()}.txt".replace(" ", "_")
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"{section['title']}\n")
        file.write("=" * len(section['title']) + "\n")
        file.write(section.get('long', "Подробная информация отсутствует.") + "\n")
    print(f"\n   📁  Раздел сохранён в файл: {filename}\n")


def display_help_menu(help_data):
    """Выводит главное меню справочной системы."""
    print("\n   📖  Справочная система")
    print("   ======================")
    for idx, section in enumerate(help_data.values(), start=1):
        print(f"   {idx}. {section['title']}")
        print(f"      {section['short']}\n")
    print("   0. Выйти из справки\n")


def display_detailed_help(section):
    """Выводит подробное описание выбранного раздела."""
    print(f"\n   {section['title']}")
    print(f"   {'=' * len(section['title'])}")
    display_message_slowly(section.get('long', "Подробная информация отсутствует."))
    print("\n   🔹 Хотите сохранить этот раздел? (y/n): ", end="")
    if input().strip().lower() == "y":
        save_help_section(section)


def interactive_help():
    """Основной цикл взаимодействия со справочной системой."""
    help_data = load_help_data()
    if not help_data:
        print("   ❌  Справочная информация недоступна.")
        return

    while True:
        display_help_menu(help_data)
        user_input = input("   Выберите номер раздела или введите ключевое слово: ").strip().lower()

        if user_input in {"0", "q", "exit"}:
            print("\n   📖  Выход из справочной системы.")
            break

        if user_input.isdigit():  # Обработка цифрового ввода
            index = int(user_input)
            if 1 <= index <= len(help_data):
                section = list(help_data.values())[index - 1]
                display_detailed_help(section)
                continue
            else:
                print("\n   ❌  Неверный выбор. Попробуйте снова.\n")
                continue

        # Поиск по ключевым словам
        matched_sections = [section for section in help_data.values()
                            if user_input in section['title'].lower() or
                            user_input in section['short'].lower() or
                            user_input in section.get('long', "").lower()]

        if len(matched_sections) == 1:
            display_detailed_help(matched_sections[0])
        elif len(matched_sections) > 1:
            print("\n   🔍  Найдено несколько совпадений:")
            for idx, section in enumerate(matched_sections, start=1):
                print(f"   {idx}. {section['title']} - {section['short']}")
            choice = input("\n   Выберите номер подходящего варианта: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(matched_sections):
                display_detailed_help(matched_sections[int(choice) - 1])
            else:
                print("\n   ❌  Неверный выбор. Попробуйте снова.")
        else:
            print("\n   ❌  Ничего не найдено. Попробуйте другой запрос.\n")


if __name__ == "__main__":
    interactive_help()
