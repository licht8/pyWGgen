#!/usr/bin/env python3
# modules/port_manager.py
# This Python script checks if a specified port is in use and offers the user actions: 
# kill the process using the port, recheck the port, or return to the main menu. 
# Utilizes the `psutil` library to retrieve information about network connections and processes. 
# Handles errors and displays appropriate messages.

import psutil
import os
import time  # Importing time module

def handle_port_conflict(port):
    """
    Checks if the port is in use and offers actions to the user.
    
    :param port: Port number to check
    :return: Action string ("kill", "restart", "exit")
    """
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                pid = conn.pid
                print(f"\n\033[1m =========================================="
                      f"\n 🚫  Port {port} is already in use \n 🐽  by a process with PID 🆔 {pid}."
                      f"\n ========================================== \033[0m")

                if pid:
                    process_name = psutil.Process(pid).name()
                    print(f"\n Process using the port: {process_name}\n 🔪 (PID {pid}).")
                else:
                    print(f" Unable to identify the process using port {port}.")

                print("\n Available actions:\n ==========================================")
                print(f" 🔪 1. Kill the process (PID {pid})")
                print(f" 🔍 2. Recheck port {port}")
                print(" 🏠 3. Return to the main menu")
                print("")
                choice = input(" Choose an action [1/2/3]: ").strip()
                
                if choice == "1" and pid:
                    try:
                        os.kill(pid, 9)
                        time.sleep(2)
                        print(f"\n ✅  Process {process_name} (PID {pid}) was 🔪 terminated 🩸.")
                        return "kill"  # Kill the process
                    except Exception as e:
                        print(f" ❌ Error terminating the process: {e}")
                elif choice == "2":
                    print(f"\n =========================================="
                          f"\n 🔍 Attempting to recheck port {port}...")
                    return "restart"  # Retry checking the port
                elif choice == "3":
                    return "exit"  # Return to the main menu
                else:
                    print(f" 🔴  Invalid choice. \n Returning to the menu.")
                    return "exit"  # Default to main menu
        return "ok"
    except Exception as e:
        print(f" ❌ Error: {e}")
        return "exit"  # Return to the main menu in case of error
