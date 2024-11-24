#!/usr/bin/env python3
# menu.py
## Меню для управления проектом wg_qr_generator

import os
import subprocess
import signal
import sys
from modules.manage_expiry import check_expiry, extend_expiry, reset_expiry
from modules.show_users import show_all_users

# Константы
ADMIN_PORT = 7860
GRADIO_ADMIN_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "gradio_admin/main_interface.py"))


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


def manage_users_menu():
    """Меню управления пользователями."""
    while True:
        print("\n========== Управление пользователями ==========")
        print("1. 🌱 Создать пользователя")
        print("2. 🔍 Показать всех пользователей")
        print("3. ❌ Удалить пользователя")
        print("4. 🔍 Проверить срок действия аккаунта")
        print("5. ➕ Продлить срок действия аккаунта")
        print("6. 🔄 Сбросить срок действия аккаунта")
        print("\n\t0 или q. Вернуться в главное меню")
        print("===============================================")
        choice = input("Выберите действие: ").strip()

        if choice in ["0", "q"]:
            print("🔙 Возврат в главное меню...")
            break

        elif choice == "1":
            nickname = input("Введите имя пользователя для создания: ").strip()
            if nickname:
                subprocess.run(["python3", "main.py", nickname])

        elif choice == "2":
            show_all_users()

        elif choice == "3":
            nickname = input("Введите имя пользователя для удаления: ").strip()
            if nickname:
                subprocess.run(["python3", "modules/manage_expiry.py", "reset", nickname])
                print(f"✅ Пользователь {nickname} успешно удален.")

        elif choice == "4":
            nickname = input("Введите имя пользователя для проверки: ").strip()
            if nickname:
                subprocess.run(["python3", "modules/manage_expiry.py", "check", nickname])

        elif choice == "5":
            nickname = input("Введите имя пользователя для продления: ").strip()
            days = input("Введите количество дней для продления: ").strip()
            if nickname and days.isdigit():
                subprocess.run(["python3", "modules/manage_expiry.py", "extend", nickname, days])

        elif choice == "6":
            nickname = input("Введите имя пользователя для сброса: ").strip()
            days = input("Введите количество дней для сброса (по умолчанию 30): ").strip()
            days = days if days.isdigit() else "30"
            if nickname:
                subprocess.run(["python3", "modules/manage_expiry.py", "reset", nickname, "--days", days])

        else:
            print("⚠️ Некорректный выбор. Попробуйте еще раз.")


def show_main_menu():
    """Главное меню."""
    while True:
        print("\n================== Меню ==================")
        print("1. 🧪 Запустить тесты")
        print("2. 🌐 Открыть Gradio админку")
        print("3. 👤 Управление пользователями")
        print("4. ♻️ Переустановить WireGuard")
        print("5. 🗑️ Удалить WireGuard")
        print("\n\t0 или q. Выход")
        print("==========================================")
        choice = input("Выберите действие: ").strip()

        if choice in ["0", "q"]:
            print("👋 Выход. До свидания!")
            break

        elif choice == "1":
            print("🧪 Запуск тестов...")
            subprocess.run(["pytest"])

        elif choice == "2":
            run_gradio_admin_interface()

        elif choice == "3":
            manage_users_menu()

        elif choice == "4":
            print("♻️ Переустановка WireGuard...")
            subprocess.run(["bash", "wireguard-install.sh"])

        elif choice == "5":
            print("🗑️ Удаление WireGuard...")
            subprocess.run(["yum", "remove", "wireguard", "-y"])

        else:
            print("⚠️ Некорректный выбор. Попробуйте еще раз.")


if __name__ == "__main__":
    show_main_menu()
