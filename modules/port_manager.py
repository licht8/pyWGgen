#!/usr/bin/env python3
# modules/port_manager.py
# Модуль для управления портами и разрешения конфликтов

import psutil
import os
import sys

def handle_port_conflict(port):
    """
    Проверяет, занят ли порт, и предлагает действия пользователю.
    
    :param port: Номер порта для проверки
    :return: Строка действия ("kill", "ignore", "exit")
    """
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                pid = conn.pid
                print("\n ")
                print(f" ⚠️ - Порт {port} уже занят процессом с PID {pid}.")
                if pid:
                    process_name = psutil.Process(pid).name()
                    print(f" Процесс, использующий порт: {process_name} 🔪 (PID {pid}).")
                else:
                    print(" Не удалось определить процесс, использующий порт.")

                print("\n Доступные действия:")
                print(f"🔪 1. Убить процесс (PID {pid})")
                print("🚫 2. Игнорировать и вернуться в меню")
                print("🚪 3. Выйти из программы")
                print("")
                choice = input(" Выберите действие [1/2/3]: ").strip()
                if choice == "1" and pid:
                    try:
                        os.kill(pid, 9)
                        print(f" ✅ Процесс {process_name} (PID {pid}) был 🔪 завершен 🩸.")
                        return "kill"
                    except Exception as e:
                        print(f" ❌ Ошибка при завершении процесса: {e}")
                elif choice == "2":
                    print(" 🔄 Возврат в меню...")
                    return "ignore"
                elif choice == "3":
                    print(" 👋 Завершение работы.")
                    exit(0)
                else:
                    print(" ⚠️ Некорректный выбор. Возврат в меню.")
                    return "ignore"
        print(f" ✅ Порт {port} свободен. (port_manager.py)")
        return "ok"
        
    except KeyboardInterrupt:
        print("\n👋 Выход из программы...")
        sys.exit(0)  # Завершение программы по "Ctrl C" без ошибки
