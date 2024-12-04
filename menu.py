#!/usr/bin/env python3
# menu.py
# Главное меню для управления проектом wg_qr_generator
# ===========================================
# Этот файл предоставляет удобный интерфейс
# для управления различными функциями проекта,
# включая установку, удаление WireGuard и многое другое.
# Версия: 1.0
# Обновлено: 2024-12-03
# ===========================================
#import pdb; pdb.set_trace()

import tracemalloc
# Запускаем мониторинг памяти с глубиной стека 10 уровней
tracemalloc.start(10)

import os
import sys
import subprocess
from modules.input_utils import input_with_history
from modules.firewall_utils import get_external_ip
from settings import LOG_DIR, LOG_FILE_PATH, DIAGNOSTICS_LOG
from modules.uninstall_wg import uninstall_wireguard
from modules.install_wg import install_wireguard
from modules.wireguard_utils import check_wireguard_installed
from ai_diagnostics.ai_diagnostics import display_message_slowly
from modules.swap_edit import check_swap_edit

# Проверка и создание swap
check_swap_edit(size_mb=512, action="micro", silent=True)

# Установить путь к корню проекта
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def initialize_project():
    """Инициализация проекта: создание необходимых директорий и файлов."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE_PATH.exists():
        LOG_FILE_PATH.touch()
        print(f"Создан пустой файл лога: {LOG_FILE_PATH}")

def show_main_menu():
    """Отображение основного меню."""
    local_print_speed = 0.005
    while True:
        wireguard_installed = check_wireguard_installed()
        display_message_slowly(f"\n🛡️  ======  Menu wg_qr_generator  ======= 🛡️\n", print_speed=local_print_speed, indent=False)
        print(f"  i. 🛠️   Информация о состоянии проекта")
        print(f"  t. 🧪  Запустить тесты")
        print(f" up. 🔄  Запустить обновление зависимостей")
        display_message_slowly(f" ------------------------------------------", print_speed=local_print_speed, indent=False)
        print(f"  g. 🌐  Открыть Gradio админку")
        print(f"  u. 👤  Управление пользователями")
        print(f" sy. 📡  Синхронизировать пользователей")
        print(f" du. 🧹  Очистить базу пользователей")
        display_message_slowly(f" ------------------------------------------", print_speed=local_print_speed, indent=False)
        if wireguard_installed:
            print(f" rw. ♻️   Переустановить WireGuard")
            print(f" dw. 🗑️   Удалить WireGuard")
        else:
            print(f" iw. ⚙️   Установить WireGuard")
        display_message_slowly(f" ------------------------------------------", print_speed=local_print_speed, indent=False)
        print(f" rg. 📋  Запустить генерацию отчета")
        print(f" sr. 🗂️   Показать краткий отчет")
        print(f" dg. 🛠️   Запустить диагностику проекта")
        print(f" fr. 📄  Показать полный отчет")
        print(f" sd. 📋  Показать журнал диагностики")
        display_message_slowly(f"\n🧩 === Раздел помощи и диагностики ==== 🧩\n", print_speed=local_print_speed, indent=False)
        print(f" aih. 🗨️  Помощь и диагностика")
        print(f" aid. 🤖 Диагностика проекта")
        print(f"\n\t 0 или q. Выход")
        display_message_slowly(f" ==========================================\n", print_speed=local_print_speed, indent=False)

        choice = input_with_history(" Выберите действие: ").strip().lower()

        if choice == "0" or choice == "q":
            print("\n 👋  Выход. До свидания!\n")
            break
        # Остальной код меню...

        # Пример обработки действий
        if choice == "i":
            from modules.project_status import show_project_status
            show_project_status()
        elif choice == "iw":
            install_wireguard()
        elif choice == "dw":
            uninstall_wireguard()
        else:
            print(f"\n  ⚠️  Некорректный выбор. Попробуйте снова.")

import tracemalloc

def main():
    # Запускаем мониторинг памяти
    tracemalloc.start()

    # Основной код программы
    initialize_project()
    show_main_menu()

    # Снимок памяти после завершения работы
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("lineno")

    # Печать топ 10 строк кода по потреблению памяти
    print("\n🔍 Топ 10 строк кода по потреблению памяти:")
    for stat in top_stats[:10]:
        print(f"{stat.traceback.format()}: size={stat.size / 1024:.2f} KB, count={stat.count}, average={stat.size / stat.count if stat.count > 0 else 0:.2f} B")

    # Сохранение отчета в файл (опционально)
    with open("memory_report.txt", "w") as f:
        f.write("\n🔍 Топ 10 строк кода по потреблению памяти:\n")
        for stat in top_stats[:10]:
            f.write(f"{stat.traceback.format()}: size={stat.size / 1024:.2f} KB, count={stat.count}, average={stat.size / stat.count if stat.count > 0 else 0:.2f} B\n")


if __name__ == "__main__":
    main()
