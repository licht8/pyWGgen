#!/usr/bin/env python3
# menu.py
# Главное меню для управления проектом wg_qr_generator

import os
import subprocess
import signal
import sys
from modules.manage_users_menu import manage_users_menu
from modules.port_manager import handle_port_conflict  # Функция для обработки конфликта портов

# Константы
WIREGUARD_BINARY = "/usr/bin/wg"
WIREGUARD_INSTALL_SCRIPT = "wireguard-install.sh"
ADMIN_PORT = 7860
GRADIO_ADMIN_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "gradio_admin/main_interface.py"))
CLEAN_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "clean_user_data.sh"))
TEST_REPORT_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_report_generator.py"))
TEST_REPORT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_report.txt"))

def check_wireguard_installed():
    """Проверка, установлен ли WireGuard."""
    return os.path.isfile(WIREGUARD_BINARY)


def install_wireguard():
    """Установка WireGuard."""
    if os.path.isfile(WIREGUARD_INSTALL_SCRIPT):
        print("  🔧  Установка WireGuard...")
        subprocess.run(["bash", WIREGUARD_INSTALL_SCRIPT])
    else:
        print(f"  ❌  Скрипт {WIREGUARD_INSTALL_SCRIPT} не найден. Положите его в текущую директорию.")


def remove_wireguard():
    """Удаление WireGuard."""
    print("  ❌  Удаление WireGuard...")
    subprocess.run(["yum", "remove", "wireguard", "-y"], stderr=subprocess.DEVNULL) or \
    subprocess.run(["apt", "remove", "wireguard", "-y"], stderr=subprocess.DEVNULL)


def open_firewalld_port(port):
    """Открытие порта через firewalld."""
    print(f"  🔓  Открытие порта {port} через firewalld...")
    try:
        subprocess.run(["sudo", "firewall-cmd", "--add-port", f"{port}/tcp"], check=True)
        print(f"  ✅  Порт {port} добавлен через firewalld (временные правила).")
    except subprocess.CalledProcessError:
        print(f"  ❌  Не удалось добавить порт {port} через firewalld.")


def close_firewalld_port(port):
    """Закрытие порта через firewalld."""
    print(f"  🔒  Закрытие порта {port} через firewalld...")
    try:
        subprocess.run(["sudo", "firewall-cmd", "--remove-port", f"{port}/tcp"], check=True)
        print(f"  ✅  Порт {port} удален через firewalld (временные правила).")
    except subprocess.CalledProcessError:
        print(f"  ❌  Не удалось удалить порт {port} через firewalld.")


def run_gradio_admin_interface():
    """Запуск Gradio интерфейса с корректной обработкой портов и сигналов выхода."""
    def handle_exit_signal(sig, frame):
        """Обработчик сигнала для закрытия порта."""
        close_firewalld_port(ADMIN_PORT)
        sys.exit(0)

    if not os.path.exists(GRADIO_ADMIN_SCRIPT):
        print(f"  ❌  Скрипт {GRADIO_ADMIN_SCRIPT} не найден.")
        return

    # Проверка наличия порта
    conflict_action = handle_port_conflict(ADMIN_PORT)
    if conflict_action == "ignore":
        return

    # Открытие порта через firewalld
    open_firewalld_port(ADMIN_PORT)

    signal.signal(signal.SIGINT, handle_exit_signal)  # Обработка Ctrl+C

    try:
        print(f"  🌐  Запуск Gradio интерфейса на порту {ADMIN_PORT}...")
        subprocess.run(["python3", GRADIO_ADMIN_SCRIPT])
    finally:
        close_firewalld_port(ADMIN_PORT)


def run_clean_user_data():
    """Запуск скрипта очистки пользовательских данных."""
    if not os.path.exists(CLEAN_SCRIPT):
        print(f"  ❌  Скрипт {CLEAN_SCRIPT} не найден.")
        return

    print("  🔄  Запуск очистки пользовательских данных...")
    subprocess.run(["bash", CLEAN_SCRIPT])


def run_test_report_generator():
    """Запуск скрипта для генерации отчета."""
    if not os.path.exists(TEST_REPORT_SCRIPT):
        print(f"  ❌  Скрипт {TEST_REPORT_SCRIPT} не найден.")
        return

    print("  📋  Запуск генерации отчета...")
    subprocess.run(["python3", TEST_REPORT_SCRIPT])


def display_test_report():
    """Вывод содержимого отчета в консоль."""
    if os.path.exists(TEST_REPORT_FILE):
        with open(TEST_REPORT_FILE, "r") as file:
            print(file.read())
    else:
        print(f"  ❌  Файл отчета {TEST_REPORT_FILE} не найден.")


def update_project_dependencies():
    """Запускает обновление проекта и зависимостей."""
    print("\n  🛠️   Обновление проекта и зависимостей...")
    try:
        # Обновление репозитория
        print("  🔄  Обновление репозитория через git...")
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        
        # Обновление зависимостей
        print("  📦  Обновление зависимостей через pip...")
        subprocess.run(["pip", "install", "-r", "requirements.txt", "--upgrade"], check=True)
        
        print("\n  ✅  Обновление проекта завершено.")
    except subprocess.CalledProcessError as e:
        print(f"  ❌  Ошибка при обновлении: {e}")
    except FileNotFoundError:
        print("  ❌  Git или pip не найдены. Убедитесь, что они установлены.")


def show_main_menu():
    """Отображение основного меню."""
    while True:
        wireguard_installed = check_wireguard_installed()
        print("\n==================  Меню  ==================\n")
        print(" 1. 🛠️   Информация о состоянии проекта")
        print(" 2. 🧪   Запустить тесты")
        print(" u. 🛠️   Запустить обновление проекта и зависимостей")
        print("--------------------------------------------")
        print(" 3. 🌐   Открыть Gradio админку")
        print(" 4. 👤   Управление пользователями")
        print("--------------------------------------------")
        if wireguard_installed:
            print(" 5. ♻️   Переустановить WireGuard")
            print(" 6. 🗑️   Удалить WireGuard")
        else:
            print(" 5. ⚙️   Установить WireGuard")
        print("--------------------------------------------")
        print(" 7. 🧹   Очистить базу пользователей")
        print(" 8. 📋   Запустить генерацию отчета")
        print(" 9. 📄   Показать отчет отладки")
        print("\n\t 0 или q. Выход")
        print(" ==========================================\n")
        
        choice = input(" Выберите действие: ").strip().lower()

        if choice == "1":
            from modules.project_status import show_project_status
            show_project_status()
        elif choice == "2":
            print("  🔍  Запуск тестов...")
            subprocess.run(["pytest"])
        elif choice == "u":
            update_project_dependencies()
        elif choice == "3":
            run_gradio_admin_interface()
        elif choice == "4":
            manage_users_menu()
        elif choice == "5":
            if wireguard_installed:
                print("  ♻️   Переустановка WireGuard...")
                remove_wireguard()
                install_wireguard()
            else:
                install_wireguard()
        elif choice == "6" and wireguard_installed:
            remove_wireguard()
        elif choice == "7":
            run_clean_user_data()
        elif choice == "8":
            run_test_report_generator()
        elif choice == "9":
            display_test_report()
        elif choice in {"0", "q"}:
            print("👋  Выход. До свидания!")
            break
        else:
            print("\n ! ⚠️  Некорректный выбор. Попробуйте снова.")

if __name__ == "__main__":
    show_main_menu()
