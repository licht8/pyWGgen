#!/usr/bin/env python3
# modules/port_manager.py
# Ten skrypt Python sprawdza czy określony port jest używany i oferuje użytkownikowi akcje: 
# zabicie procesu używającego portu, ponowne sprawdzenie portu lub powrót do menu głównego. 
# Używa biblioteki `psutil` do pobierania informacji o połączeniach sieciowych i procesach. 
# Obsługuje błędy i wyświetla odpowiednie komunikaty.

import psutil
import os
import time  # Import modułu time

def handle_port_conflict(port):
    """
    Sprawdza czy port jest używany i oferuje użytkownikowi akcje.
    
    :param port: Numer portu do sprawdzenia
    :return: Ciąg akcji ("kill", "restart", "exit")
    """
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                pid = conn.pid
                print(f"\n\033[1m =========================================="
                      f"\n 🚫  Port {port} jest już używany \n 🐽  przez proces z PID 🆔 {pid}."
                      f"\n ========================================== \033[0m")

                if pid:
                    process_name = psutil.Process(pid).name()
                    print(f"\n Proces używający portu: {process_name}\n 🔪 (PID {pid}).")
                else:
                    print(f" Nie można zidentyfikować procesu używającego portu {port}.")

                print("\n Dostępne akcje:\n ==========================================")
                print(f" 🔪 1. Zabij proces (PID {pid})")
                print(f" 🔍 2. Ponownie sprawdź port {port}")
                print(" 🏠 3. Powrót do menu głównego")
                print("")
                choice = input(" Wybierz akcję [1/2/3]: ").strip()
                
                if choice == "1" and pid:
                    try:
                        os.kill(pid, 9)
                        time.sleep(2)
                        print(f"\n ✅  Proces {process_name} (PID {pid}) został 🔪 zakończony 🩸.")
                        return "kill"  # Zabij proces
                    except Exception as e:
                        print(f" ❌ Błąd zakończenia procesu: {e}")
                elif choice == "2":
                    print(f"\n =========================================="
                          f"\n 🔍 Próba ponownego sprawdzenia portu {port}...")
                    return "restart"  # Ponów sprawdzenie portu
                elif choice == "3":
                    return "exit"  # Powrót do menu głównego
                else:
                    print(f" 🔴  Nieprawidłowy wybór. \n Powrót do menu.")
                    return "exit"  # Domyślnie do menu głównego
        return "ok"
    except Exception as e:
        print(f" ❌ Błąd: {e}")
        return "exit"  # Powrót do menu głównego w przypadku błędu
