#!/usr/bin/env python3
# menu.py
# Главное меню для управления проектом wg_qr_generator

import os
import sys
import subprocess
import psutil

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
from modules.update_utils import update_project
from modules.sync import sync_users_with_wireguard
from modules.manage_users_menu import manage_users_menu
from modules.debugger import run_diagnostics  # Исправленный импорт функции диагностики


def show_main_menu():
    """Отображение основного меню."""
    while True:
        wireguard_installed = check_wireguard_installed()
        print("\n==================  Меню  ==================\n")
        print(" 1. 🛠️    Информация о состоянии проекта")
        print(" 2. 🧪   Запустить тесты")
        print(" u. 🔄   Запустить обновление проекта и зависимостей")
        print("--------------------------------------------")
        print(" 3. 🌐   Открыть Gradio админку")
        print(" 4. 👤   Управление пользователями")
        print("11. 🔄   Синхронизировать пользователей")
        print("--------------------------------------------")
        if wireguard_installed:
            print(" 5. ♻️   Переустановить WireGuard")
            print(" 6. 🗑️   Удалить WireGuard")
        else:
            print(" 5. ⚙️   Установить WireGuard")
        print(f"--------------------------------------------")
        print(f" 7. 🧹   Очистить базу пользователей")
        print(f" 8. 📋   Запустить генерацию отчета")
        print(f" 9. 🗂️    Показать краткий отчет")
        print(f"10. 📄   Показать полный отчет")
        print(f"12. 🛠️   Запустить диагностику проекта")  # Новый пункт меню
        print(f"\n\t 0 или q. Выход")
        print(f" ==========================================\n")
        
        choice = input(" Выберите действие: ").strip().lower()

        if choice == "1":
            from modules.project_status import show_project_status
            show_project_status()
        elif choice == "2":
            print("🔍  Запуск тестов...")
            subprocess.run(["pytest"])
        elif choice == "u":
            update_project()

        elif choice == "3":
            # Проверяем, занят ли порт перед запуском Gradio
            port = 7860
            action = handle_port_conflict(port)  # Проверяем состояние порта
            if action == "ok":
                print(f" ✅ Порт {port} свободен, запускаем Gradio...")
                run_gradio_admin_interface(port=port)
            elif action == "kill":
                print(" ✅ Процесс был завершен, теперь можно запустить Gradio.")
                run_gradio_admin_interface(port=port)
            elif action == "restart":
                print(f" 🔄 Порт {port} все еще занят. Пожалуйста, проверьте его снова.\n ==========================================\n ")
            elif action == "exit":
                print(f"\n 🔙 Возврат в главное меню.")
        elif choice == "4":
            manage_users_menu()
        elif choice == "5":
            remove_wireguard()
            install_wireguard()
        elif choice == "6" and wireguard_installed:
            remove_wireguard()
        elif choice == "7":
            from modules.user_data_cleaner import clean_user_data
            clean_user_data()
        elif choice == "8":
            generate_project_report()
        elif choice == "9":
            display_test_summary()
        elif choice == "10":
            display_test_report()
        elif choice == "11":
            sync_users_with_wireguard()
        elif choice == "12":
            print("🔍  Запуск диагностики проекта...")
            run_diagnostics()  # Вызов функции диагностики
        elif choice in {"0", "q"}:
            print("\n 👋  Выход. До свидания!\n")
            break
        else:
            print("\n ! ⚠️  Некорректный выбор. Попробуйте снова.")

if __name__ == "__main__":
    show_main_menu()
