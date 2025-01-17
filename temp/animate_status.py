import os
import sys
import subprocess
import threading
import time

# Добавляем текущий и родительский каталог в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


loading = False  # Глобальная переменная для управления лоадером

def start_loader(message="Processing"):
    """Функция запуска лоадера."""
    global loading
    loading = True
    spinner = ["🌕", "🌖", "🌗", "🌘", "🌑", "🌒", "🌓", "🌔"]
    idx = 0
    while loading:
        print(f"\r{message} {spinner[idx % len(spinner)]}", end="", flush=True)
        idx += 1
        time.sleep(0.2)

def stop_loader():
    """Останавливает лоадер и очищает строку."""
    global loading
    loading = False
    print("\r", end="", flush=True)  # Удаляет лоадер с экрана
