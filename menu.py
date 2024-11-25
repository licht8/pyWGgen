#!/usr/bin/env python3
# menu.py
# Главное меню для управления проектом wg_qr_generator

import sys
import os
import subprocess
from modules.wireguard_utils import check_wireguard_installed, install_wireguard, remove_wireguard
from modules.firewall_utils import open_firewalld_port, close_firewalld_port
from modules.gradio_utils import run_gradio_admin_interface
from modules.report_utils import generate_project_report, display_test_report, display_test_summary
from modules.update_utils import update_project
from modules.sync import sync_users_with_wireguard
from modules.manage_users_menu import manage_users_menu

def show_main_menu():
    """Отображение основного меню."""
    while True:
        wireguard_installed = check_wireguard_installed()
        print("\n==================  Меню  ==================\n")
        print(" 1. 🛠️   Информация о состоянии проекта")
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
        print("--------------------------------------------")
        print(" 7. 🧹   Очистить базу пользователей")
        print(" 8. 📋   Запустить генерацию отчета")
        print(" 9. 🗂️   Показать краткий отчет")
        print("10. 📄   Показать полный отчет")
        print("\n\t 0 или q. Выход")
        print(" ==========================================\n")
        
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
            run_gradio_admin_interface()
        elif choice == "4":
            manage_users_menu()
        elif choice == "5":
            remove_wireguard()
            install_wireguard()
        elif choice == "6" and wireguard_installed:
            remove_wireguard()
        elif choice == "7":
            from modules.user_data_cleaner import clean_user_data  # Импорт функции очистки
            clean_user_data()
        elif choice == "8":
            generate_project_report()
        elif choice == "9":
            display_test_summary()
        elif choice == "10":
            display_test_report()
        elif choice == "11":
            sync_users_with_wireguard()
        elif choice in {"0", "q"}:
            print("👋  Выход. До свидания!")
            break
        else:
            print("\n ! ⚠️  Некорректный выбор. Попробуйте снова.")

if __name__ == "__main__":
    show_main_menu()
