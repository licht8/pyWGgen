#!/usr/bin/env python3
# ai_diagnostics/ai_help/ai_help.py
# Справочная система для проекта wg_qr_generator.
# Версия: 2.6
# Обновлено: 2024-12-04

import json
import sys
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

# Загрузка глобальных настроек проекта
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SETTINGS_FILE = PROJECT_ROOT / "settings.py"

# Определяем пути для модулей и других компонентов
MODULES_DIR = PROJECT_ROOT / "modules"
HELP_DIR = PROJECT_ROOT / "ai_diagnostics" / "ai_help"

# Добавляем пути в `sys.path` для корректного импорта
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(MODULES_DIR))

# Загружаем глобальные настройки
def load_settings():
    """Загружает настройки из settings.py."""
    settings = {}
    if SETTINGS_FILE.exists():
        spec = spec_from_file_location("settings", SETTINGS_FILE)
        settings_module = module_from_spec(spec)
        spec.loader.exec_module(settings_module)
        settings = {key: getattr(settings_module, key) for key in dir(settings_module) if not key.startswith("__")}
    return settings

SETTINGS = load_settings()

# Подключение зависимостей
try:
    from modules.input_utils import input_with_history
    from ai_diagnostics.ai_diagnostics import display_message_slowly
except ModuleNotFoundError as e:
    print(f"Ошибка импорта модуля: {e}")
    print("Проверьте структуру проекта и пути к модулям.")
    sys.exit(1)

# Конфигурация форматирования текста
LINE_WIDTH = {
    "menu": 60,
    "details": 70
}

# Функции для работы со справочной системой
def wrap_text(text, width, indent=4):
    """Форматирует текст по ширине строки с заданным отступом."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 > width:
            lines.append(" " * indent + current_line)
            current_line = word
        else:
            current_line += ("" if current_line == "" else " ") + word

    if current_line:
        lines.append(" " * indent + current_line)

    return "\n".join(lines)

def preserve_json_formatting(text, indent=4):
    """Форматирует текст, сохраняя отступы и переносы из JSON."""
    lines = []
    for line in text.split("\n"):
        if line.strip():
            lines.append(" " * indent + line)
        else:
            lines.append("")
    return "\n".join(lines)

def replace_variables(text):
    """Заменяет переменные вида {VARIABLE} на значения из SETTINGS."""
    for key, value in SETTINGS.items():
        text = text.replace(f"{{{key}}}", str(value))
    return text

def load_help_files():
    """Загружает все JSON файлы из HELP_DIR."""
    help_data = {}
    for json_file in HELP_DIR.rglob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                help_data.update(data)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки файла {json_file}: {e}")
    return help_data

def display_help_menu(help_data):
    """Выводит главное меню справочной системы."""
    print("\n   📖  Справочная система")
    print("   ======================")
    for idx, section in enumerate(help_data.values(), start=1):
        print(f"   {idx}. {section['title']}")
        print(wrap_text(section['short'], LINE_WIDTH["menu"], indent=6) + "\n")
    print("   0. Выйти из справки\n")

def display_detailed_help(section):
    """Выводит подробное описание выбранного раздела."""
    print(f"\n   {section['title']}\n")
    print(f"   {'=' * len(section['title'])}\n")
    formatted_text = replace_variables(section.get('long', "Подробная информация отсутствует."))
    formatted_text = preserve_json_formatting(formatted_text)
    display_message_slowly(formatted_text)

def interactive_help():
    """Основной цикл справочной системы."""
    help_data = load_help_files()
    if not help_data:
        print("   ❌ Справочная информация недоступна.")
        return

    while True:
        display_help_menu(help_data)
        user_input = input("   Выберите номер раздела или введите ключевое слово: ").strip().lower()

        if user_input in {"0", "q", "exit"}:
            print("\n   📖 Выход из справочной системы.")
            break

        if user_input.isdigit():
            index = int(user_input)
            if 1 <= index <= len(help_data):
                section = list(help_data.values())[index - 1]
                display_detailed_help(section)
        else:
            matches = [s for s in help_data.values() if user_input in s['title'].lower()]
            if matches:
                if len(matches) == 1:
                    display_detailed_help(matches[0])
                else:
                    print("🔍 Найдено несколько совпадений. Уточните запрос.")

if __name__ == "__main__":
    interactive_help()
