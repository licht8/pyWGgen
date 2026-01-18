#!/usr/bin/env python3
# menu.py
# Menu główne do zarządzania projektem pyWGgen
# ===========================================
# Ten plik zapewnia wygodny interfejs
# do zarządzania różnymi funkcjami projektu,
# w tym instalacją, usuwaniem WireGuard i więcej.
# Wersja: 1.2
# Zaktualizowano: 2026-01-10
# ===========================================

import os
import time
import sys
import subprocess
from modules.input_utils import input_with_history
from modules.firewall_utils import get_external_ip
from settings import LOG_DIR, LOG_FILE_PATH, DIAGNOSTICS_LOG, PRINT_SPEED
from modules.uninstall_wg import uninstall_wireguard
from modules.install_wg import install_wireguard
from modules.wireguard_utils import check_wireguard_installed
from modules.swap_edit import check_swap_edit, swap_edit
from modules.report_utils import create_summary_report

# Stała LINE_DELAY
LINE_DELAY = 0.05


def display_message_slowly(message, print_speed=None, end="\n", indent=True):
    """
    Wyświetla wiadomość linia po linii z opcjonalnym wcięciem i niestandardową prędkością.

    :param message: Wiadomość do wyświetlenia.
    :param print_speed: Prędkość wyświetlania znaków (w sekundach). Jeśli None, używana jest globalna PRINT_SPEED.
    :param end: Znak końcowy linii (domyślnie: "\\n").
    :param indent: Jeśli True, dodaje 3-spacjowe wcięcie przed każdą linią.
    """
    effective_speed = print_speed if print_speed is not None else PRINT_SPEED
    for line in message.split("\n"):
        if indent:
            print("   ", end="")  # Dodaj wcięcie jeśli indent=True
        for char in line:
            print(char, end="", flush=True)
            time.sleep(effective_speed)
        print(end, end="", flush=True)
        time.sleep(LINE_DELAY)


# Sprawdź i utwórz plik swap o rozmiarze 512 MB jeśli potrzeba
check_swap_edit(size_mb=512, action="micro", silent=True)

# Ustaw ścieżkę główną projektu
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def show_diagnostics_log():
    """Wyświetla dziennik diagnostyczny."""
    if os.path.exists(DIAGNOSTICS_LOG):
        print("\n === 🛠️  Dziennik diagnostyczny  ===\n")
        with open(DIAGNOSTICS_LOG, "r") as log_file:
            print(log_file.read())
    else:
        print("\n ❌  Dziennik diagnostyczny nie został znaleziony.\n")


def initialize_project():
    """Inicjalizuje projekt: tworzy niezbędne katalogi i pliki."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE_PATH.exists():
        LOG_FILE_PATH.touch()
        print(f"Utworzono pusty plik dziennika: {LOG_FILE_PATH}")


# Wywołaj funkcję inicjalizacji
initialize_project()
create_summary_report()


def show_main_menu():
    """Wyświetl menu główne."""
    local_print_speed = 0.005
    while True:
        wireguard_installed = check_wireguard_installed()
        display_message_slowly(f"\n🛡️  ======  Menu pyWGgen  ======= 🛡️\n", print_speed=local_print_speed, indent=False)
        display_message_slowly(f" ------------------------------------------", print_speed=local_print_speed, indent=False)
        print(f"  g. 🌐  Otwórz Panel Administracyjny Gradio")
        print(f"  u. 👤  Zarządzaj Użytkownikami")
        print(f" sy. 📡  Synchronizuj Użytkowników")
        print(f" du. 🧹  Wyczyść Bazę Użytkowników")
        display_message_slowly(f" ------------------------------------------", print_speed=local_print_speed, indent=False)
        if wireguard_installed:
            print(f" rw. ♻️   Przeinstaluj WireGuard")
            print(f" dw. 🗑️   Usuń WireGuard")
        else:
            print(f" iw. ⚙️   Zainstaluj WireGuard")
        print(f" up. 🔄  Aktualizuj Zależności")
        display_message_slowly(f" ------------------------------------------", print_speed=local_print_speed, indent=False)
        print(f"  s. 📊  Status Projektu i Raport")
        print(f"  d. 🛠️   Diagnostyka Systemu")

        display_message_slowly(f"\n🤖  ======  Asystent AI   ======  🤖\n", print_speed=local_print_speed, indent=False)
        print(f" aid. 🚀  Diagnostyka VPN z AI")
        print(f" aic. 💬  Czat z AI")
        print(f" air. 📄  Generuj Raport z AI")

        print(f"\n\t 0 lub q. Wyjście")
        display_message_slowly(f" =========================================""\n", print_speed=local_print_speed, indent=False)

        choice = input_with_history(" Wybierz akcję: ").strip().lower()

        if choice in {"0", "q"}:
            print("\n 👋  Wyjście. Do widzenia!\n")
            break

        # Status Projektu i Raport (połączone: i + rg + fr)
        elif choice == "s":
            from modules.report_utils import display_summary_report, show_project_status, generate_project_report, display_test_report
            print("\n📊 Generowanie statusu projektu...\n")
            try:
                display_summary_report()
                show_project_status()
                print("\n📋 Pełny raport:\n")
                generate_project_report()
                display_test_report()
            except Exception as e:
                print(f"⚠️  Błąd: {e}")
            input("\n Naciśnij Enter aby kontynuować...")

        # Diagnostyka Systemu (połączone: dg + sd)
        elif choice == "d":
            from modules.debugger import run_diagnostics
            print("\n🛠️  Uruchamianie diagnostyki...\n")
            try:
                run_diagnostics()
                print("\n📜 Dziennik diagnostyczny:\n")
                show_diagnostics_log()
            except Exception as e:
                print(f"⚠️  Błąd: {e}")
            input("\n Naciśnij Enter aby kontynuować...")

        # Aktualizuj Zależności
        elif choice == "up":
            from modules.update_utils import update_project
            update_project()

        # Panel Administracyjny Gradio
        elif choice == "g":
            from modules.gradio_utils import run_gradio_admin_interface
            port = 7860
            print(f"\n ✅  Uruchamianie interfejsu Gradio http://{get_external_ip()}:{port}")
            run_gradio_admin_interface(port=port)

        # Zarządzaj Użytkownikami
        elif choice == "u":
            from modules.manage_users_menu import manage_users_menu
            manage_users_menu()

        # Przeinstaluj WireGuard
        elif choice == "rw":
            install_wireguard()

        # Zainstaluj WireGuard
        elif choice == "iw":
            install_wireguard()

        # Usuń WireGuard
        elif choice == "dw":
            uninstall_wireguard()

        # Wyczyść Bazę Użytkowników
        elif choice == "du":
            from modules.user_data_cleaner import clean_user_data
            clean_user_data()

        # Synchronizuj Użytkowników
        elif choice == "sy":
            from modules.sync import sync_users_from_config
            sync_users_from_config()

        # ========== ASYSTENT AI ==========
        # Diagnostyka VPN z AI (Pełna)
        elif choice == "aid":
            print("\n🚀 Uruchamianie Diagnostyki VPN z AI...\n")
            try:
                subprocess.run(["python3", "ai_assistant/diagnostics.py"])
            except Exception as e:
                print(f"⚠️  Błąd: {e}")
            input("\n Naciśnij Enter aby kontynuować...")

        # Tryb Czatu z AI
        elif choice == "aic":
            print("\n💬 Uruchamianie Czatu z AI...\n")
            try:
                from ai_assistant.data_collector import collect_all_data
                from ai_assistant.ai_chat import interactive_mode
                print("🔄 Zbieranie danych serwera VPN...")
                data = collect_all_data()
                print("✅ Dane zebrane. Uruchamianie czatu...\n")
                interactive_mode(data)
            except Exception as e:
                print(f"⚠️  Błąd: {e}")
            input("\n Naciśnij Enter aby kontynuować...")

        # Generowanie Raportu z AI
        elif choice == "air":
            print("\n📄 Uruchamianie Generatora Raportów AI...\n")
            try:
                from ai_assistant.data_collector import collect_all_data
                from ai_assistant.ai_report import show_report_menu
                print("🔄 Zbieranie danych do raportu...")
                data = collect_all_data()
                show_report_menu(data)
            except Exception as e:
                print(f"⚠️  Błąd: {e}")
            input("\n Naciśnij Enter aby kontynuować...")
        # ==================================

        else:
            print(f"\n  ⚠️  Nieprawidłowy wybór. Spróbuj ponownie.")


def main():
    """Funkcja główna."""
    initialize_project()
    show_main_menu()


if __name__ == "__main__":
    main()
