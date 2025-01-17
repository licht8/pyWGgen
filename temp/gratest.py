#!/usr/bin/env python3
# gratest.py

import os
import subprocess
import sys

def open_firewalld_port(port):
    """Открытие порта через firewalld."""
    print(f"🔓 Открытие порта {port} через firewalld...")
    subprocess.run(["firewall-cmd", "--zone=public", "--add-port", f"{port}/tcp"], check=False)
    subprocess.run(["firewall-cmd", "--zone=public", "--add-port", f"{port}/udp"], check=False)
    print("success")

def close_firewalld_port(port):
    """Закрытие порта через firewalld."""
    print(f"🔒 Закрытие порта {port} через firewalld...")
    subprocess.run(["firewall-cmd", "--zone=public", "--remove-port", f"{port}/tcp"], check=False)
    subprocess.run(["firewall-cmd", "--zone=public", "--remove-port", f"{port}/udp"], check=False)
    print("success")

def run_gradio_interface():
    """Запуск Gradio интерфейса."""
    port = 7860
    try:
        open_firewalld_port(port)
        print(f"🌐  Запуск Gradio интерфейса на порту {port}...")
        # Добавление PYTHONPATH и запуск
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()
        subprocess.run(["python3", "gradio_admin/main_interface.py"], env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при запуске Gradio интерфейса: {e}")
    finally:
        close_firewalld_port(port)

def main_menu():
    """Основное меню."""
    while True:
        print("\n=== Меню управления wg_qr_generator ===")
        print("1. 🔄 Перезапустить проект")
        print("2. 🛠️  Запустить диагностику проекта")
        print("3. 🌐 Запустить Gradio интерфейс")
        print("0. Выход")
        choice = input("Введите номер действия: ").strip()

        if choice == "1":
            print("Перезапуск проекта...")
            subprocess.run(["./run_project.sh"])
        elif choice == "2":
            print("Запуск диагностики...")
            subprocess.run(["python3", "modules/debugger.py"])
        elif choice == "3":
            run_gradio_interface()
        elif choice in {"0", "q", "exit"}:
            print("Выход из программы.")
            sys.exit(0)
        else:
            print("❌ Неверный ввод. Попробуйте снова.")

if __name__ == "__main__":
    main_menu()
