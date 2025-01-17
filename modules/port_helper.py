#!/usr/bin/env python3
# modules/port_helper.py
# Utility for checking and managing ports

import os
import signal
import psutil

def check_port_and_handle(port):
    """
    Checks if the specified port is in use and offers actions to the user.
    
    :param port: Port number to check.
    :return: None
    """
    for conn in psutil.net_connections(kind="inet"):
        if conn.laddr.port == port:
            pid = conn.pid
            if pid is not None:
                process = psutil.Process(pid)
                print(f"⚠️ Port {port} is already in use by the following process:")
                print(f" - PID: {pid}")
                print(f" - Process name: {process.name()}")
                print(f" - Command: {' '.join(process.cmdline())}\n")

                choice = input("Choose an action: [k] Kill process / [i] Ignore and exit: ").strip().lower()
                if choice == "k":
                    try:
                        os.kill(pid, signal.SIGKILL)
                        print(f"✅ Process with PID {pid} terminated successfully.")
                    except Exception as e:
                        print(f"❌ Error terminating process: {e}")
                else:
                    print("🔙 Returning to menu.")
                    return False
            else:
                print(f"⚠️ Port {port} is in use, but the process ID could not be determined.")
                return False
    return True
