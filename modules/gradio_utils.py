#!/usr/bin/env python3
# modules/gradio_utils.py
# Модуль для работы с Gradio

import os
import signal
import subprocess
import sys
from modules.firewall_utils import open_firewalld_port, close_firewalld_port

ADMIN_PORT = 7860
GRADIO_ADMIN_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gradio_admin/main_interface.py"))

def run_gradio_admin_interface():
    """Запуск Gradio интерфейса с корректной обработкой портов и сигналов выхода."""
    def handle_exit_signal(sig, frame):
        """Обработчик сигнала для закрытия порта."""
        close_firewalld_port(ADMIN_PORT)
        sys.exit(0)

    if not os.path.exists(GRADIO_ADMIN_SCRIPT):
        print(f"  ❌  Скрипт {GRADIO_ADMIN_SCRIPT} не найден.")
        return

    open_firewalld_port(ADMIN_PORT)
    signal.signal(signal.SIGINT, handle_exit_signal)  # Обработка Ctrl+C

    try:
        print(f"  🌐  Запуск Gradio интерфейса на порту {ADMIN_PORT}...")
        subprocess.run(["python3", GRADIO_ADMIN_SCRIPT])
    finally:
        close_firewalld_port(ADMIN_PORT)
