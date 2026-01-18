#!/usr/bin/env python3
# modules/port_helper.py
# Narzędzie do sprawdzania i zarządzania portami

import os
import signal
import psutil

def check_port_and_handle(port):
    """
    Sprawdza czy określony port jest używany i oferuje użytkownikowi akcje.
    
    :param port: Numer portu do sprawdzenia.
    :return: None
    """
    for conn in psutil.net_connections(kind="inet"):
        if conn.laddr.port == port:
            pid = conn.pid
            if pid is not None:
                process = psutil.Process(pid)
                print(f"⚠️ Port {port} jest już używany przez następny proces:")
                print(f" - PID: {pid}")
                print(f" - Nazwa procesu: {process.name()}")
                print(f" - Komenda: {' '.join(process.cmdline())}\n")

                choice = input("Wybierz akcję: [k] Zabij proces / [i] Ignoruj i wyjdź: ").strip().lower()
                if choice == "k":
                    try:
                        os.kill(pid, signal.SIGKILL)
                        print(f"✅ Proces z PID {pid} zakończony pomyślnie.")
                    except Exception as e:
                        print(f"❌ Błąd zakończenia procesu: {e}")
                else:
                    print("🔙 Powrót do menu.")
                    return False
            else:
                print(f"⚠️ Port {port} jest używany, ale nie można określić ID procesu.")
                return False
    return True
