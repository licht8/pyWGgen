#!/usr/bin/env python3
# menu.py
# Главное меню для управления проектом wg_qr_generator

import os
import sys
import subprocess
from modules.firewall_utils import get_external_ip
from settings import LOG_DIR, LOG_FILE_PATH, DIAGNOSTICS_LOG

# Установить путь к корню проекта
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Импорт модулей
from modules.wireguard_utils import check_wireguard_installed, install_wireguard, remove_wireguard
from modules.firewall_utils import open_firewalld_port, close_firewalld_port
from modules.gradio_utils import run_gradio_admin_interface
from modules.port_manager import handle_port_conflict
from modules.report_utils import generate_project_report, display_test_report, display_test_summary
from modules.report_utils import display_summary_report
from modules.update_utils import update_project
from modules.sync import sync_users_with_wireguard
from modules.manage_users_menu import manage_users_menu
from modules.debugger import run_diagnostics
from ai_diagnostics.ai_diagnostics import display_message_slowly


# Проверяем и создаем директории и файлы
def initialize_project():
    """Инициализация проекта: создание необходимых директорий и файлов."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)  # Создает директорию, если ее нет
    if not LOG_FILE_PATH.exists():
        LOG_FILE_PATH.touch()  # Создает пустой файл, если он отсутствует
        print(f"Создан пустой файл лога: {LOG_FILE_PATH}")

# Вызов функции инициализации
initialize_project()

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
        display_message_slowly(f"\n🛡️  ======  Menu wg_qr_generator  ======= 🛡️\n", print_speed=local_print_speed, indent=False)  # Передаем локальную скорость Без отступов
        print(f"  i. 🛠️   Информация о состоянии проекта")
        print(f"  t. 🧪  Запустить тесты")
        print(f" up. 🔄  Запустить обновление зависимостей")
        display_message_slowly(f" ------------------------------------------", print_speed=local_print_speed, indent=False)  # Передаем локальную скорость Без отступов
        print(f"  g. 🌐  Открыть Gradio админку")
        print(f"  u. 👤  Управление пользователями")
        print(f" sy. 📡  Синхронизировать пользователей")
        print(f" du. 🧹  Очистить базу пользователей")
        display_message_slowly(f" ------------------------------------------", print_speed=local_print_speed, indent=False)  # Передаем локальную скорость Без отступов
        if wireguard_installed:
            print(f" rw. ♻️   Переустановить WireGuard")
            print(f" dw. 🗑️   Удалить WireGuard")
        else:
            print(f" iw. ⚙️   Установить WireGuard")
        display_message_slowly(f" ------------------------------------------", print_speed=local_print_speed, indent=False)  # Передаем локальную скорость Без отступов
        print(f" rg. 📋  Запустить генерацию отчета")
        print(f" sr. 🗂️   Показать краткий отчет")
        print(f" dg. 🛠️   Запустить диагностику проекта")
        print(f" fr. 📄  Показать полный отчет")
        print(f" sd. 📋  Показать журнал диагностики")
        display_message_slowly(f"\n🧩 === Раздел помощи и диагностики ==== 🧩\n", print_speed=local_print_speed, indent=False)  # Передаем локальную скорость Без отступов
        print(f" aih. 🗨️  Помощь и диагностика")
        print(f" aid. 🤖 Диагностика проекта")
        print(f"\n\t 0 или q. Выход")
        display_message_slowly(f" ==========================================\n", print_speed=local_print_speed, indent=False)  # Передаем локальную скорость Без отступов Нижняя граница

        choice = input(" Выберите действие: ").strip().lower()
        # Обработка выбора...


        if choice == "i":
            from modules.project_status import show_project_status
            show_project_status()
        elif choice == "t":
            print(f" 🔍  Запуск тестов...")
            subprocess.run(["pytest"])
        elif choice == "up":
            update_project()
        elif choice == "g":
            port = 7860
            action = handle_port_conflict(port)
            if action == "ok":
                print(f"\n ✅  Запускаем Gradio интерфейс http://{get_external_ip()}:{port}")
                run_gradio_admin_interface(port=port)
            elif action == "kill":
                print(f" ✅  Теперь запускаем Gradio http://{get_external_ip()}:{port}.")
                run_gradio_admin_interface(port=port)
            elif action == "restart":
                print(f" 🚫 Порт {port} все еще занят.")
            elif action == "exit":
                print(f"\n 🔙 Возврат в главное меню.")
        elif choice == "u":
            manage_users_menu()
        elif choice == "rw":
            remove_wireguard()
            install_wireguard()
        elif choice == "iw" and wireguard_installed:
            remove_wireguard()
        elif choice == "du":
            from modules.user_data_cleaner import clean_user_data
            clean_user_data()
        elif choice == "rg":
            print(f" 🔍  Генерация полного отчета...")
            generate_project_report()
        elif choice == "sr":
            print(f" 📂  Отображение краткого отчета...")
            display_summary_report()
        elif choice == "fr":
            print(f" 📄  Отображение полного отчета...")
            display_test_report()
        elif choice == "sy":
            sync_users_with_wireguard()
        elif choice == "dg":
            print(f" 🔍  Запуск диагностики проекта...")
            run_diagnostics()
        elif choice == "sd":
            print(f" 📋  Показ журнала диагностики...")
            show_diagnostics_log()
        elif choice == "aih":
            print(f" 🤖  Запуск справочной системы...")
            os.system("python3 ai_diagnostics/ai_help/ai_help.py")
        elif choice == "aid":
            print(f"\n    🤖  Запуск интерактивной диагностики проекта...")
            os.system("python3 ai_diagnostics/ai_diagnostics.py")
        elif choice in {"0", "q"}:
            print("\n 👋  Выход. До свидания!\n")
            break
        else:
            print(f"\n  ⚠️  Некорректный выбор. Попробуйте снова.")


if __name__ == "__main__":
    show_main_menu()
