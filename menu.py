#!/usr/bin/env python3
# menu.py
## Меню для управления проектом wg_qr_generator
# Предоставляет интерфейс для управления VPN, запуска тестов, основного скрипта и Gradio админки.

import os
import subprocess
import signal
import sys

# Константы
WIREGUARD_BINARY = "/usr/bin/wg"
WIREGUARD_INSTALL_SCRIPT = "wireguard-install.sh"
CONFIG_DIR = "user/data"
TEST_USER = "test_user"
ADMIN_PORT = 7860
GRADIO_ADMIN_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "gradio_admin/main_interface.py"))


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


def ensure_test_config_exists():
    """Создание тестовой конфигурации, если она отсутствует."""
    config_path = os.path.join(CONFIG_DIR, f"{TEST_USER}.conf")
    if not os.path.exists(config_path):
        print("⚙️  Тестовая конфигурация отсутствует. Создаём тестового пользователя...")
        subprocess.run(["python3", "main.py", TEST_USER])
        print(f"✅ Тестовый пользователь '{TEST_USER}' успешно создан.")
    else:
        print(f"✅ Тестовая конфигурация '{TEST_USER}' уже существует.")


def open_firewalld_port(port):
    """Открытие порта через firewalld."""
    print(f"🔓 Открытие порта {port} через firewalld...")
    subprocess.run(["sudo", "firewall-cmd", "--add-port", f"{port}/tcp", "--permanent"])
    subprocess.run(["sudo", "firewall-cmd", "--reload"])
    print(f"✅ Порт {port} открыт через firewalld.")


def close_firewalld_port(port):
    """Закрытие порта через firewalld."""
    print(f"🔒 Закрытие порта {port} через firewalld...")
    subprocess.run(["sudo", "firewall-cmd", "--remove-port", f"{port}/tcp", "--permanent"])
    subprocess.run(["sudo", "firewall-cmd", "--reload"])
    print(f"✅ Порт {port} закрыт через firewalld.")


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


def show_menu():
    """Отображение меню."""
    while True:
        wireguard_installed = check_wireguard_installed()
        print("================== Меню ==================")
        print("1. Запустить тесты")
        print("2. Запустить основной скрипт (main.py)")
        print("3. Открыть Gradio админку")
        if wireguard_installed:
            print("4. Переустановить WireGuard ♻️")
            print("5. Удалить WireGuard 🗑️")
        else:
            print("4. Установить WireGuard ⚙️")
        print("0. Выход")
        print("==========================================")
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            # Проверяем наличие тестовой конфигурации перед тестами
            ensure_test_config_exists()
            print("🔍 Запуск тестов...")
            subprocess.run(["pytest"])
        elif choice == "2":
            nickname = input("Введите имя пользователя (nickname): ").strip()
            subprocess.run(["python3", "main.py", nickname])
        elif choice == "3":
            run_gradio_admin_interface()
        elif choice == "4":
            install_wireguard()
        elif choice == "5":
            if wireguard_installed:
                remove_wireguard()
            else:
                print("⚠️ WireGuard не установлен.")
        elif choice == "0":
            print("👋 Выход. До свидания!")
            break
        else:
            print("⚠️ Некорректный выбор. Попробуйте еще раз.")


if __name__ == "__main__":
    show_menu()
