#!/usr/bin/env python3
# menu.py
# Меню для управления проектом wg_qr_generator

import os
import subprocess
import signal
import sys

# Константы
WIREGUARD_BINARY = "/usr/bin/wg"
WIREGUARD_INSTALL_SCRIPT = "wireguard-install.sh"
CONFIG_DIR = "user/data"
ADMIN_PORT = 7860
GRADIO_ADMIN_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "gradio_admin/main_interface.py"))

# Добавляем текущий каталог в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Импортируем подменю
from modules.manage_expiry import check_expiry, extend_expiry, reset_expiry
from modules.show_users import show_all_users


def check_wireguard_installed():
    """Проверка, установлен ли WireGuard."""
    return os.path.isfile(WIREGUARD_BINARY)


def install_wireguard():
    """Установка WireGuard."""
    if os.path.isfile(WIREGUARD_INSTALL_SCRIPT):
        print("🔧 Установка WireGuard...")
        subprocess.run(["bash", WIREGUARD_INSTALL_SCRIPT])
    else:
        print(f"❌ Скрипт {WIREGUARD_INSTALL_SCRIPT} не найден. Положите его в текущую директорию.")


def remove_wireguard():
    """Удаление WireGuard."""
    print("❌ Удаление WireGuard...")
    subprocess.run(["yum", "remove", "wireguard", "-y"], stderr=subprocess.DEVNULL) or \
    subprocess.run(["apt", "remove", "wireguard", "-y"], stderr=subprocess.DEVNULL)


def open_firewalld_port(port):
    """Открытие порта через firewalld."""
    print(f"🔓 Открытие порта {port} через firewalld...")
    try:
        subprocess.run(["sudo", "firewall-cmd", "--add-port", f"{port}/tcp"], check=True)
        print(f"✅ Порт {port} добавлен через firewalld (временные правила).")
    except subprocess.CalledProcessError:
        print(f"❌ Не удалось добавить порт {port} через firewalld.")


def close_firewalld_port(port):
    """Закрытие порта через firewalld."""
    print(f"🔒 Закрытие порта {port} через firewalld...")
    try:
        subprocess.run(["sudo", "firewall-cmd", "--remove-port", f"{port}/tcp"], check=True)
        print(f"✅ Порт {port} удален через firewalld (временные правила).")
    except subprocess.CalledProcessError:
        print(f"❌ Не удалось удалить порт {port} через firewalld.")


def run_gradio_admin_interface():
    """Запуск Gradio интерфейса с корректной обработкой Ctrl+C."""
    def handle_exit_signal(sig, frame):
        """Обработчик сигнала для закрытия порта."""
        close_firewalld_port(ADMIN_PORT)
        sys.exit(0)

    if not os.path.exists(GRADIO_ADMIN_SCRIPT):
        print(f"❌ Скрипт {GRADIO_ADMIN_SCRIPT} не найден.")
        return

    # Проверка и открытие порта
    open_firewalld_port(ADMIN_PORT)
    signal.signal(signal.SIGINT, handle_exit_signal)  # Обработка Ctrl+C

    try:
        print(f"🌐 Запуск Gradio интерфейса на порту {ADMIN_PORT}...")
        subprocess.run(["python3", GRADIO_ADMIN_SCRIPT])
    finally:
        close_firewalld_port(ADMIN_PORT)


def manage_user_menu():
    """Подменю для управления пользователями."""
    while True:
        print("\n========== Управление пользователями ==========")
        print("1. 🌱 Создать пользователя")
        print("2. 📋 Показать всех пользователей")
        print("3. 🔥 Удалить пользователя")
        print("4. 🔍 Проверить срок действия аккаунта")
        print("5. ⏳ Продлить срок действия аккаунта")
        print("6. ♻️  Сбросить срок действия аккаунта")
        print("\n\t0 или q. Вернуться в главное меню")
        print("===============================================")
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            nickname = input("Введите имя пользователя (nickname): ").strip()
            subprocess.run(["python3", "main.py", nickname])
        elif choice == "2":
            show_all_users()
        elif choice == "3":
            nickname = input("Введите имя пользователя для удаления: ").strip()
            # Здесь нужно добавить функцию удаления пользователя
            print(f"🔧 Удаление пользователя {nickname} не реализовано.")
        elif choice == "4":
            nickname = input("Введите имя пользователя для проверки срока: ").strip()
            try:
                result = check_expiry(nickname)
                print(result)
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        elif choice == "5":
            nickname = input("Введите имя пользователя для продления срока: ").strip()
            days = input("Введите количество дней для продления: ").strip()
            try:
                extend_expiry(nickname, int(days))
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        elif choice == "6":
            nickname = input("Введите имя пользователя для сброса срока: ").strip()
            try:
                reset_expiry(nickname)
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        elif choice in ["0", "q"]:
            print("🔙 Возврат в главное меню...")
            break
        else:
            print("⚠️ Некорректный выбор. Попробуйте еще раз.")


def show_menu():
    """Отображение главного меню."""
    while True:
        wireguard_installed = check_wireguard_installed()
        print("\n================== Меню ==================")
        print("1. 🧪 Запустить тесты")
        print("2. 🌐 Открыть Gradio админку")
        print("3. 👥 Управление пользователями")
        print("4. ♻️ Переустановить WireGuard")
        print("5. 🗑️ Удалить WireGuard")
        print("\n\t0 или q. Выход")
        print("==========================================")
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            print("🔍 Запуск тестов...")
            subprocess.run(["pytest"])
        elif choice == "2":
            run_gradio_admin_interface()
        elif choice == "3":
            manage_user_menu()
        elif choice == "4":
            install_wireguard()
        elif choice == "5":
            if wireguard_installed:
                remove_wireguard()
            else:
                print("⚠️ WireGuard не установлен.")
        elif choice in ["0", "q"]:
            print("👋 Выход. До свидания!")
            break
        else:
            print("⚠️ Некорректный выбор. Попробуйте еще раз.")


if __name__ == "__main__":
    show_menu()
