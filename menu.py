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
import time
import sys
import subprocess
from modules.input_utils import input_with_history  # Импортируем нашу функцию
from modules.firewall_utils import get_external_ip
from settings import LOG_DIR, LOG_FILE_PATH, DIAGNOSTICS_LOG
from modules.uninstall_wg import uninstall_wireguard
from modules.install_wg import install_wireguard  # Импортируем функцию install_wireguard
# Импорт модулей
from modules.wireguard_utils import check_wireguard_installed
from ai_diagnostics.ai_diagnostics import display_message_slowly
from modules.swap_edit import check_swap_edit, swap_edit

from modules.swap_edit import check_swap_edit

# Проверить и создать swap размером 64 MB, если необходимо
check_swap_edit(size_mb=512, action="micro", silent=True)


# Установить путь к корню проекта
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def show_diagnostics_log():
    """Отображает содержимое журнала диагностики."""
    if os.path.exists(DIAGNOSTICS_LOG):
        print("\n === 🛠️  Журнал диагностики  ===\n")
        with open(DIAGNOSTICS_LOG, "r") as log_file:
            print(log_file.read())
    else:
        print("\n ❌  Журнал диагностики отсутствует.\n")



# Проверяем и создаем директории и файлы
def initialize_project():
    """Инициализация проекта: создание необходимых директорий и файлов."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)  # Создает директорию, если ее нет
    if not LOG_FILE_PATH.exists():
        LOG_FILE_PATH.touch()  # Создает пустой файл, если он отсутствует
        print(f"Создан пустой файл лога: {LOG_FILE_PATH}")


# Вызов функции инициализации
initialize_project()


def show_main_menu():
    """Отображение основного меню."""
    local_print_speed = 0.005  # Локальная скорость печати
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
        print(f" rg. 📋  Генерация отчета о состоянии проекта")
        print(f" fr. 📄  Показать отчет о состоянии проекта")
        print(f" dg. 🛠️   Запустить диагностику проекта")
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


        if choice == "i":
            from modules.report_utils import display_summary_report, show_project_status
            display_summary_report()
            show_project_status()
        elif choice == "t":
            print(f" 🔍  Запуск тестов...")
            subprocess.run(["pytest"])
        elif choice == "up":
            from modules.update_utils import update_project
            update_project()
        elif choice == "g":
            from modules.gradio_utils import run_gradio_admin_interface
            port = 7860
            print(f"\n ✅  Запускаем Gradio интерфейс http://{get_external_ip()}:{port}")
            run_gradio_admin_interface(port=port)
        elif choice == "u":
            from modules.manage_users_menu import manage_users_menu
            manage_users_menu()
        elif choice == "rw":
            install_wireguard()
        elif choice == "iw":
            install_wireguard()
        elif choice == "dw":
            uninstall_wireguard()
        elif choice == "du":
            from modules.user_data_cleaner import clean_user_data
            clean_user_data()
        elif choice == "rg":
            from modules.report_utils import generate_project_report
            generate_project_report()
        elif choice == "fr":
            from modules.report_utils import display_test_report
            display_test_report()
            time.sleep(2)
        elif choice == "sy":
            from modules.sync import sync_users_with_wireguard
            sync_users_with_wireguard()
        elif choice == "dg":
            from modules.debugger import run_diagnostics
            run_diagnostics()
        elif choice == "sd":
            show_diagnostics_log()
            time.sleep(2)
        elif choice == "aih":
            os.system("python3 ai_diagnostics/ai_help/ai_help.py")
        elif choice == "aid":
            os.system("python3 ai_diagnostics/ai_diagnostics.py")
        elif choice in {"0", "q"}:
            print("\n 👋  Выход. До свидания!\n")
            break
        else:
            print(f"\n  ⚠️  Некорректный выбор. Попробуйте снова.")

import tracemalloc

def main():
    # Запускаем мониторинг памяти
    tracemalloc.start(10)

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
        #print(stat)

    # Сохранение отчета в файл (опционально)
    with open("memory_report.txt", "w") as f:
        f.write("\n🔍 Топ 10 строк кода по потреблению памяти:\n")
        for stat in top_stats[:10]:
            f.write(f"{stat.traceback.format()}: size={stat.size / 1024:.2f} KB, count={stat.count}, average={stat.size / stat.count if stat.count > 0 else 0:.2f} B\n")


if __name__ == "__main__":
    main()

#if __name__ == "__main__":
#    show_main_menu()
