#!/usr/bin/env python3
# gradio_utils.py
# Утилиты для запуска Gradio интерфейса.

import os
import subprocess

def run_gradio_admin_interface():
    """Запуск Gradio интерфейса на 0.0.0.0:7860."""
    port = 7860
    print(f"🔓 Открытие порта {port} через firewalld...")
    subprocess.run(["firewall-cmd", "--zone=public", "--add-port", f"{port}/tcp"], check=False)
    subprocess.run(["firewall-cmd", "--zone=public", "--add-port", f"{port}/udp"], check=False)
    print("success")
    
    try:
        print("🌐  Запуск Gradio интерфейса...")
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()  # Установить текущую директорию как PYTHONPATH
        subprocess.run(
            ["python3", "gradio_admin/main_interface.py", "--server_port", str(port), "--server_name", "0.0.0.0"],
            env=env,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при запуске Gradio интерфейса: {e}")
    finally:
        print(f"🔒 Закрытие порта {port} через firewalld...")
        subprocess.run(["firewall-cmd", "--zone=public", "--remove-port", f"{port}/tcp"], check=False)
        subprocess.run(["firewall-cmd", "--zone=public", "--remove-port", f"{port}/udp"], check=False)
        print("success")
