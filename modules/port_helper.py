#!/usr/bin/env python3
# modules/port_helper.py
# Утилита для проверки и управления портами

import os
import signal
import psutil

def check_port_and_handle(port):
    """
    Проверяет, занят ли указанный порт, и предлагает действия пользователю.
    
    :param port: Номер порта для проверки.
    :return: None
    """
    for conn in psutil.net_connections(kind="inet"):
        if conn.laddr.port == port:
            pid = conn.pid
            if pid is not None:
                process = psutil.Process(pid)
                print(f"⚠️ Порт {port} уже занят процессом:")
                print(f" - PID: {pid}")
                print(f" - Имя процесса: {process.name()}")
                print(f" - Команда: {' '.join(process.cmdline())}\n")

                choice = input("Выберите действие: [k] Убить процесс / [i] Игнорировать и выйти: ").strip().lower()
                if choice == "k":
                    try:
                        os.kill(pid, signal.SIGKILL)
                        print(f"✅ Процесс PID {pid} успешно завершен.")
                    except Exception as e:
                        print(f"❌ Ошибка при завершении процесса: {e}")
                else:
                    print("🔙 Возврат в меню.")
                    return False
            else:
                print(f"⚠️ Порт {port} занят, но идентификатор процесса не определен.")
                return False
    return True
