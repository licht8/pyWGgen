#!/usr/bin/env python3
# ai_diagnostics/ai_help/ai_help.py
# Справочная система для проекта pyWGgen.
# Версия: 2.6
# Обновлено: 2024-12-04
# Новое:
# - Поддержка истории ввода и движения по ней с использованием стрелок.


import json
import sys
import logging
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

# Устанавливаем пути для проекта
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODULES_DIR = PROJECT_ROOT / "ai_diagnostics" / "modules"
HELP_DIR = PROJECT_ROOT / "ai_diagnostics" / "ai_help"
SETTINGS_FILE = PROJECT_ROOT / "settings.py"

sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(MODULES_DIR))

# Настройка логирования
LOG_FILE = PROJECT_ROOT / "user/data/logs/app.log"
LOG_LEVEL = logging.DEBUG  # Уровень логирования: DEBUG, INFO, WARNING, ERROR

logging.basicConfig(
    filename=LOG_FILE,
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Импорты
try:
    from pause_rules import apply_pause, get_pause_rules  # Исправленный путь к pause_rules
    from ai_diagnostics.ai_diagnostics import display_message_slowly
    from modules.input_utils import input_with_history  # Корректный импорт input_utils
except ImportError as e:
    logging.error(f"❌ Ошибка импорта модуля: {e}")
    print(f"❌ Ошибка импорта модуля: {e}")
    sys.exit(1)

# Конфигурация для форматирования текста
LINE_WIDTH = {
    "menu": 60,
    "details": 70
}



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
    """Форматирует текст, полностью сохраняя оригинальные отступы и переносы из JSON."""
    lines = []
    for line in text.split("\n"):
        if line.strip():  # Если строка не пустая, добавляем отступ
            lines.append(" " * indent + line)
        else:  # Если строка пустая, добавляем пустую строку без отступов
            lines.append("")
    return "\n".join(lines)


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


def replace_variables(text):
    """Заменяет переменные вида {VARIABLE} на значения из SETTINGS."""
    for key, value in SETTINGS.items():
        text = text.replace(f"{{{key}}}", str(value))
    return text


def load_help_files():
    """Загружает все JSON файлы из HELP_DIR."""
    logging.debug(f"Проверяем директорию справки: {HELP_DIR}")
    help_data = {}
    for json_file in HELP_DIR.rglob("*.json"):
        try:
            logging.debug(f"Обрабатываем файл справки: {json_file}")
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                for key, section in data.items():
                    if "title" not in section or ("short" not in section and "long" not in section):
                        logging.warning(f"⚠️ Проблема в разделе '{key}': отсутствует один из ключей ('title', 'short', 'long').")
                help_data.update(data)
        except Exception as e:
            logging.error(f"⚠️ Ошибка загрузки файла {json_file}: {e}")
    return help_data


def save_help_section(section):
    """Сохраняет раздел справки в файл."""
    filename = f"{section['title'].strip()}.txt".replace(" ", "_")
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"{section['title']}\n")
        file.write("=" * len(section['title']) + "\n")
        file.write(wrap_text(section.get('long', "Подробная информация отсутствует."), LINE_WIDTH["details"]) + "\n")
    print(f"\n   📁  Раздел сохранён в файл: {filename}\n")


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
    if 'long' not in section:
        logging.warning(f"⚠️ Проблема в разделе '{section['title']}': отсутствует ключ 'long'.")
        print(f"⚠️ Проблема в разделе '{section['title']}': отсутствует ключ 'long'.")
        return

    # Заголовок
    print(f"\n   {section['title']}\n")
    print(f"   {'=' * (len(section['title'].strip()) + 4)}\n")

    # Замена переменных и сохранение форматирования
    formatted_text = replace_variables(section.get('long', "Подробная информация отсутствует."))
    formatted_text = preserve_json_formatting(formatted_text)

    # Вывод текста
    display_message_slowly(formatted_text)

    # Сохранение раздела
    print("\n   🔹 Хотите сохранить этот раздел? ( д/н ): ", end="")
    user_input = input_with_history("").strip().lower()
    if user_input in {"д", "y"}:
        save_help_section(section)
    elif user_input in {"0", "q"}:
        print("\n   📖  Возврат в главное меню.")


def interactive_help():
    """Основной цикл взаимодействия со справочной системой."""
    help_data = load_help_files()
    if not help_data:
        print("   ❌  Справочная информация недоступна.")
        return

    while True:
        display_help_menu(help_data)
        user_input = input_with_history("   Выберите номер раздела или введите ключевое слово: ").strip().lower()

        if user_input in {"0", "q", "exit"}:
            print("\n   📖  Выход из справочной системы.")
            break

        if user_input.isdigit():  # Проверяем, является ли ввод числом
            index = int(user_input)
            if 1 <= index <= len(help_data):  # Если это номер раздела
                section = list(help_data.values())[index - 1]
                display_detailed_help(section)
                continue
        else:  # Поиск по тексту
            matches = [
                section for section in help_data.values()
                if user_input in section['title'].lower() or
                user_input in section['short'].lower() or
                user_input in section.get('long', "").lower()
            ]

            if len(matches) == 1:
                display_detailed_help(matches[0])
            elif len(matches) > 1:
                display_help_menu({"matches": matches})
            else:
                print("\n   ❌  Ничего не найдено. Попробуйте другой запрос.\n")


if __name__ == "__main__":
    interactive_help()
