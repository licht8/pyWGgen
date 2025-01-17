#!/usr/bin/env python3
# menu.py
# Main menu for managing the pyWGgen project
# ===========================================
# This file provides a convenient interface
# for managing various project functions,
# including WireGuard installation, removal, and more.
# Version: 1.0
# Updated: 2024-12-03
# ===========================================

#import pdb; pdb.set_trace()

#import tracemalloc
# Start memory monitoring with stack depth of 10 levels
#tracemalloc.start(10)

import os
import time
import sys
import subprocess
from modules.input_utils import input_with_history  # Importing our function
from modules.firewall_utils import get_external_ip
from settings import LOG_DIR, LOG_FILE_PATH, DIAGNOSTICS_LOG
from modules.uninstall_wg import uninstall_wireguard
from modules.install_wg import install_wireguard  # Importing the install_wireguard function
# Module imports
from modules.wireguard_utils import check_wireguard_installed
from ai_diagnostics.ai_diagnostics import display_message_slowly
from modules.swap_edit import check_swap_edit, swap_edit
from modules.report_utils import create_summary_report
from modules.swap_edit import check_swap_edit

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

# Check and create directories and files
def initialize_project():
    """Initialize the project: create necessary directories and files."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist
    if not LOG_FILE_PATH.exists():
        LOG_FILE_PATH.touch()  # Create an empty file if it doesn't exist
        print(f"Created an empty log file: {LOG_FILE_PATH}")

# Call the initialization function
initialize_project()
create_summary_report()

def show_main_menu():
    """Display the main menu."""
    local_print_speed = 0.005  # Local print speed
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
        print(f"  i. 🛠️   Project Status Information")
        print(f" rg. 📋  Generate Project Status Report")
        print(f" fr. 📄  Show Project Status Report")
        print(f" dg. 🛠️   Run Project Diagnostics")
        print(f" sd. 📋  Show Diagnostics Log")
        print(f"  t. 🧪  Run Tests")

        display_message_slowly(f"\n🧩 === Help and Diagnostics Section ==== 🧩\n", print_speed=local_print_speed, indent=False)
        print(f" aih. 🗨️  Help and Diagnostics")
        print(f" aid. 🤖 Run Project Diagnostics")
        print(f"\n\t 0 or q. Exit")
        display_message_slowly(f" ==========================================""\n", print_speed=local_print_speed, indent=False)

        choice = input_with_history(" Select an action: ").strip().lower()

        if choice == "0" or choice == "q":
            print("\n 👋  Exiting. Goodbye!\n")
            break

        if choice == "i":
            from modules.report_utils import display_summary_report, show_project_status
            display_summary_report()
            show_project_status()
        elif choice == "t":
            print(f" 🔍  Running tests...")
            subprocess.run(["pytest"])
        elif choice == "up":
            from modules.update_utils import update_project
            update_project()
        elif choice == "g":
            from modules.gradio_utils import run_gradio_admin_interface
            port = 7860
            print(f"\n ✅  Launching Gradio interface http://{get_external_ip()}:{port}")
            run_gradio_admin_interface(port=port)
        elif choice == "u":
            from modules.manage_users_menu import manage_users_menu
            manage_users_menu()
        elif choice == "rw":
            install_wireguard()
        elif choice == "iw":
            install_wireguard()
        elif choice == "dw":
            uninstall_wireguard()
        elif choice == "du":
            from modules.user_data_cleaner import clean_user_data
            clean_user_data()
        elif choice == "rg":
            from modules.report_utils import generate_project_report
            generate_project_report()
        elif choice == "fr":
            from modules.report_utils import display_test_report
            display_test_report()
            time.sleep(2)
        elif choice == "sy":
            from modules.sync import sync_users_from_config
            sync_users_from_config()
        elif choice == "dg":
            from modules.debugger import run_diagnostics
            run_diagnostics()
        elif choice == "sd":
            show_diagnostics_log()
            time.sleep(2)
        elif choice == "aih":
            os.system("python3 ai_diagnostics/ai_help/ai_help.py")
        elif choice == "aid":
            os.system("python3 ai_diagnostics/ai_diagnostics.py")
        elif choice in {"0", "q"}:
            print("\n 👋  Exiting. Goodbye!\n")
            break
        else:
            print(f"\n  ⚠️  Invalid choice. Please try again.")

import tracemalloc

def main():
    # Start memory monitoring
    #tracemalloc.start(10)

    # Main program code
    initialize_project()
    show_main_menu()

    # Memory snapshot after completion
    #snapshot = tracemalloc.take_snapshot()
    #top_stats = snapshot.statistics("lineno")

    # Print top 10 lines of code by memory consumption
    #print("\n🔍 Top 10 lines of code by memory usage:")
    #for stat in top_stats[:10]:
        #print(f"{stat.traceback.format()}: size={stat.size / 1024:.2f} KB, count={stat.count}, average={stat.size / stat.count if stat.count > 0 else 0:.2f} B")
        #print(stat)

    # Save report to file (optional)
    #with open("memory_report.txt", "w") as f:
        #f.write("\n🔍 Top 10 lines of code by memory usage:\n")
       # for stat in top_stats[:10]:
           # f.write(f"{stat.traceback.format()}: size={stat.size / 1024:.2f} KB, count={stat.count}, average={stat.size / stat.count if stat.count > 0 else 0:.2f} B\n")

if __name__ == "__main__":
    main()

#if __name__ == "__main__":
#    show_main_menu()
