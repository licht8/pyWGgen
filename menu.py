#!/usr/bin/env python3
# menu.py
# Main menu for managing the pyWGgen project
# ===========================================
# This file provides a convenient interface
# for managing various project functions,
# including WireGuard installation, removal, and more.
# Version: 1.2
# Updated: 2026-01-10
# ===========================================

import os
import time
import sys
import subprocess
from modules.input_utils import input_with_history
from modules.firewall_utils import get_external_ip
from settings import LOG_DIR, LOG_FILE_PATH, DIAGNOSTICS_LOG
from modules.uninstall_wg import uninstall_wireguard
from modules.install_wg import install_wireguard
from modules.wireguard_utils import check_wireguard_installed
from ai_diagnostics.ai_diagnostics import display_message_slowly
from modules.swap_edit import check_swap_edit, swap_edit
from modules.report_utils import create_summary_report

# Check and create a swap file of size 512 MB if needed
check_swap_edit(size_mb=512, action="micro", silent=True)

# Set the project root path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def show_diagnostics_log():
    """Displays the diagnostics log."""
    if os.path.exists(DIAGNOSTICS_LOG):
        print("\n === 🛠️  Diagnostics Log  ===\n")
        with open(DIAGNOSTICS_LOG, "r") as log_file:
            print(log_file.read())
    else:
        print("\n ❌  Diagnostics log not found.\n")


def initialize_project():
    """Initialize the project: create necessary directories and files."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE_PATH.exists():
        LOG_FILE_PATH.touch()
        print(f"Created an empty log file: {LOG_FILE_PATH}")


# Call the initialization function
initialize_project()
create_summary_report()


def show_main_menu():
    """Display the main menu."""
    local_print_speed = 0.005
    while True:
        wireguard_installed = check_wireguard_installed()
        display_message_slowly(f"\n🛡️  ======  Menu pyWGgen  ======= 🛡️\n", print_speed=local_print_speed, indent=False)
        display_message_slowly(f" ------------------------------------------", print_speed=local_print_speed, indent=False)
        print(f"  g. 🌐  Open Gradio Admin Panel")
        print(f"  u. 👤  Manage Users")
        print(f" sy. 📡  Synchronize Users")
        print(f" du. 🧹  Clear User Database")
        display_message_slowly(f" ------------------------------------------", print_speed=local_print_speed, indent=False)
        if wireguard_installed:
            print(f" rw. ♻️   Reinstall WireGuard")
            print(f" dw. 🗑️   Remove WireGuard")
        else:
            print(f" iw. ⚙️   Install WireGuard")
        print(f" up. 🔄  Update Dependencies")
        display_message_slowly(f" ------------------------------------------", print_speed=local_print_speed, indent=False)
        print(f"  s. 📊  Project Status & Report")
        print(f"  d. 🛠️   System Diagnostics")

        display_message_slowly(f"\n🤖  ======  AI Assistant   ======  🤖\n", print_speed=local_print_speed, indent=False)
        print(f" aid. 🚀  AI VPN Diagnostics")
        print(f" aic. 💬  AI Chat")
        print(f" air. 📄  AI Generate Report")
        
        print(f"\n\t 0 or q. Exit")
        display_message_slowly(f" ==========================================""\n", print_speed=local_print_speed, indent=False)

        choice = input_with_history(" Select an action: ").strip().lower()

        if choice in {"0", "q"}:
            print("\n 👋  Exiting. Goodbye!\n")
            break

        # Project Status & Report (объединено: i + rg + fr)
        elif choice == "s":
            from modules.report_utils import display_summary_report, show_project_status, generate_project_report, display_test_report
            print("\n📊 Generating project status...\n")
            try:
                display_summary_report()
                show_project_status()
                print("\n📋 Full report:\n")
                generate_project_report()
                display_test_report()
            except Exception as e:
                print(f"⚠️  Error: {e}")
            input("\n Press Enter to continue...")

        # System Diagnostics (объединено: dg + sd)
        elif choice == "d":
            from modules.debugger import run_diagnostics
            print("\n🛠️  Running diagnostics...\n")
            try:
                run_diagnostics()
                print("\n📜 Diagnostics log:\n")
                show_diagnostics_log()
            except Exception as e:
                print(f"⚠️  Error: {e}")
            input("\n Press Enter to continue...")

        # Update Dependencies
        elif choice == "up":
            from modules.update_utils import update_project
            update_project()

        # Gradio Admin Panel
        elif choice == "g":
            from modules.gradio_utils import run_gradio_admin_interface
            port = 7860
            print(f"\n ✅  Launching Gradio interface http://{get_external_ip()}:{port}")
            run_gradio_admin_interface(port=port)

        # Manage Users
        elif choice == "u":
            from modules.manage_users_menu import manage_users_menu
            manage_users_menu()

        # Reinstall WireGuard
        elif choice == "rw":
            install_wireguard()

        # Install WireGuard
        elif choice == "iw":
            install_wireguard()

        # Remove WireGuard
        elif choice == "dw":
            uninstall_wireguard()

        # Clear User Database
        elif choice == "du":
            from modules.user_data_cleaner import clean_user_data
            clean_user_data()

        # Synchronize Users
        elif choice == "sy":
            from modules.sync import sync_users_from_config
            sync_users_from_config()

        # ========== AI ASSISTANT ==========
        # AI VPN Diagnostics (Full)
        elif choice == "aid":
            print("\n🚀 Запуск AI VPN Diagnostics...\n")
            try:
                subprocess.run(["python3", "ai_assistant/diagnostics.py"])
            except Exception as e:
                print(f"⚠️  Error: {e}")
            input("\n Press Enter to continue...")
        
        # AI Chat Mode
        elif choice == "aic":
            print("\n💬 Запуск AI Chat...\n")
            try:
                from ai_assistant.data_collector import collect_all_data
                from ai_assistant.ai_chat import interactive_mode
                print("🔄 Сбор данных VPN сервера...")
                data = collect_all_data()
                print("✅ Данные собраны. Запуск чата...\n")
                interactive_mode(data)
            except Exception as e:
                print(f"⚠️  Error: {e}")
            input("\n Press Enter to continue...")
        
        # AI Generate Report
        elif choice == "air":
            print("\n📄 Запуск AI Report Generator...\n")
            try:
                from ai_assistant.data_collector import collect_all_data
                from ai_assistant.ai_report import show_report_menu
                print("🔄 Сбор данных для отчёта...")
                data = collect_all_data()
                show_report_menu(data)
            except Exception as e:
                print(f"⚠️  Error: {e}")
            input("\n Press Enter to continue...")
        # ==================================
        
        else:
            print(f"\n  ⚠️  Invalid choice. Please try again.")


def main():
    """Main function."""
    initialize_project()
    show_main_menu()


if __name__ == "__main__":
    main()
