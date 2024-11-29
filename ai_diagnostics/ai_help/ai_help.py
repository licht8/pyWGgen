#!/usr/bin/env python3
# ai_diagnostics/ai_help/ai_help.py
# Справочная система для проекта wg_qr_generator.
# Версия: 2.2
# Обновлено: 2024-11-29

import json
import sys
from pathlib import Path

# Добавляем пути к корню проекта и модулям
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODULES_DIR = PROJECT_ROOT / "ai_diagnostics" / "modules"
HELP_DIR = PROJECT_ROOT / "ai_diagnostics" / "ai_help"

sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(MODULES_DIR))

# Импорты
from pause_rules import apply_pause, get_pause_rules
from ai_diagnostics.ai_diagnostics import display_message_slowly

# Конфигурация для форматирования текста
LINE_WIDTH = {
    "menu": 60,
    "details": 70
}

def wrap_text(text, width, indent=4):
    """
    Форматирует текст по ширине строки с сохранением форматирования из JSON.

    Args:
        text (str): Исходный текст.
        width (int): Максимальная ширина строки.
        indent (int): Отступ в пробелах.

    Returns:
        str: Отформатированный текст.
    """
    lines = []
    current_line = ""
    indent_str = " " * indent

    for line in text.split("\n"):
        words = line.split()
        for word in words:
            if len(current_line) + len(word) + 1 > width:
                lines.append(f"{indent_str}{current_line}")
                current_line = word
            else:
                current_line += ("" if current_line == "" else " ") + word
        if current_line:
            lines.append(f"{indent_str}{current_line}")
            current_line = ""

    return "\n".join(lines)

def load_help_files():
    """Загружает все JSON файлы из HELP_DIR."""
    help_data = {}
    for json_file in HELP_DIR.rglob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                for key, section in data.items():
                    if "title" not in section or "short" not in section or "long" not in section:
                        print(f"⚠️  Проблема в разделе '{key}': отсутствует один из ключей ('title', 'short', 'long').")
                help_data.update(data)
        except Exception as e:
            print(f"⚠️  Ошибка загрузки файла {json_file}: {e}")
    return help_data

def save_help_section(section):
    """Сохраняет раздел справки в файл."""
    filename = f"{section['title'].strip()}.txt".replace(" ", "_")
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"{section['title']}\n")
        file.write(f"{'=' * len(section['title'])}\n")
        file.write(f"{wrap_text(section.get('long', 'Подробная информация отсутствует.'), LINE_WIDTH['details'])}\n")
    print(f"\n   📁  Раздел сохранён в файл: {filename}\n")

def display_help_menu(help_data):
    """Выводит главное меню справочной системы."""
    print(f"\n   📖  Справочная система")
    print(f"   ======================")
    for idx, section in enumerate(help_data.values(), start=1):
        print(f"   {idx}. {section['title']}")
        print(f"{wrap_text(section['short'], LINE_WIDTH['menu'], indent=6)}\n")
    print(f"   0. Выйти из справки\n")

def display_detailed_help(section):
    """Выводит подробное описание выбранного раздела."""
    if 'long' not in section:
        print(f"⚠️  Проблема в разделе '{section['title']}': отсутствует ключ 'long'.")
        return
    
    # Заголовок с равномерными отступами
    print(f"\n   {section['title']}\n")
    print(f"   {'=' * (len(section['title'].strip()) + 4)}\n")  # Линия разделителя с отступами
    
    # Обрабатываем текст, включая \n и списки
    formatted_text = section.get('long', "Подробная информация отсутствует.")
    formatted_text = formatted_text.replace("\n", "\n\n")  # Добавляем двойные переводы строк для видимого пропуска
    formatted_text = formatted_text.replace('1️⃣', '  1️⃣').replace('2️⃣', '  2️⃣').replace('💡', '  💡')
    
    # Форматируем текст с учётом ширины и отступов
    formatted_text = wrap_text(formatted_text, LINE_WIDTH["details"], indent=6)
    
    # Выводим текст с замедлением
    display_message_slowly(formatted_text)
    
    print("\n   🔹 Хотите сохранить этот раздел? ( д/н ): ", end="")
    user_input = input().strip().lower()
    if user_input in {"д", "y"}:
        save_help_section(section)
    elif user_input in {"0", "q"}:
        print("\n   📖  Возврат в главное меню.")


def search_in_matches(matches):
    """Обрабатывает повторный поиск в найденных совпадениях."""
    while True:
        print(f"\n   🔍  Найдено несколько совпадений:")
        for idx, section in enumerate(matches, start=1):
            print(f"   {idx}. {section['title']}")
            print(f"{wrap_text(section['short'], LINE_WIDTH['menu'], indent=6)}\n")

        user_input = input(f"\n   Введите номер варианта или уточняющее ключевое слово: ").strip().lower()

        if user_input.isdigit():
            index = int(user_input)
            if 1 <= index <= len(matches):
                return matches[index - 1]
            else:
                print(f"\n   ❌  Неверный выбор. Попробуйте снова.")
        else:
            matches = [section for section in matches
                       if user_input in section['title'].lower() or
                       user_input in section['short'].lower() or
                       user_input in section.get('long', "").lower()]
            if len(matches) == 1:
                return matches[0]
            elif not matches:
                print(f"\n   ❌  Ничего не найдено. Попробуйте другой запрос.")
                break

def interactive_help():
    """Основной цикл взаимодействия со справочной системой."""
    help_data = load_help_files()
    if not help_data:
        print(f"   ❌  Справочная информация недоступна.")
        return

    while True:
        display_help_menu(help_data)
        user_input = input(f"   Выберите номер раздела или введите ключевое слово: ").strip().lower()

        if user_input in {"0", "q", "exit"}:
            print(f"\n   📖  Выход из справочной системы.")
            break

        if user_input.isdigit():
            index = int(user_input)
            if 1 <= index <= len(help_data):
                section = list(help_data.values())[index - 1]
                display_detailed_help(section)
                continue

        matched_sections = [section for section in help_data.values()
                            if user_input in section['title'].lower() or
                            user_input in section['short'].lower() or
                            user_input in section.get('long', "").lower()]

        if len(matched_sections) == 1:
            display_detailed_help(matched_sections[0])
        elif len(matched_sections) > 1:
            matches = search_in_matches(matched_sections)
            if matches:
                display_detailed_help(matches)
        else:
            print(f"\n   ❌  Ничего не найдено. Попробуйте другой запрос.\n")

if __name__ == "__main__":
    interactive_help()
