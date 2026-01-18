#!/usr/bin/env python3
"""
get_memory_usage_by_scripts.py
Skrypt do analizy zużycia pamięci projektu pyWGgen z szczegółowym podziałem.
"""

import psutil
import os
import sys
import time
import gc
import objgraph
from pathlib import Path
from memory_profiler import memory_usage

# Dodajemy katalog główny projektu do sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
sys.path.append(str(PROJECT_DIR))

# Import ustawień projektu
try:
    from settings import BASE_DIR
except ImportError:
    print("❌ Nie można znaleźć settings.py. Upewnij się, że plik znajduje się w katalogu głównym projektu.")
    sys.exit(1)


def get_memory_usage_by_scripts(project_dir):
    """
    Zbiera informacje o zużyciu pamięci dla skryptów projektu i sortuje według zużycia pamięci.
    
    Args:
        project_dir (str): Katalog główny projektu.

    Returns:
        list: Posortowana lista procesów z ich zużyciem pamięci.
    """
    project_dir = os.path.abspath(project_dir)
    processes_info = []

    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline', 'memory_info', 'cwd']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            cmdline = proc.info['cmdline']
            cwd = proc.info.get('cwd')  # Aktualny katalog roboczy procesu
            memory_usage = proc.info['memory_info'].rss  # Zużycie pamięci w bajtach

            # Sprawdza czy proces należy do projektu
            if (
                cmdline and any(project_dir in arg for arg in cmdline)
                or (cwd and project_dir in cwd)
            ):
                processes_info.append({
                    'pid': pid,
                    'name': name,
                    'cmdline': ' '.join(cmdline),
                    'memory_usage': memory_usage,
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Sortuje procesy według zużycia pamięci malejąco
    sorted_processes = sorted(processes_info, key=lambda x: x['memory_usage'], reverse=True)
    return sorted_processes


def analyze_memory_objects():
    """
    Analizuje obiekty w pamięci, wyświetlając ich wzrost i zużycie pamięci.
    """
    print("\n🔍 Analiza aktywnych obiektów:")
    print("Typ obiektu           Liczba")
    print("-" * 50)
    for obj_type, count in objgraph.most_common_types(limit=10):
        print(f"{obj_type:<25}{count}")

    print("\n🔍 Wzrost obiektów:")
    objgraph.show_growth(limit=10)


def display_memory_usage(project_dir, interval=1):
    """
    Wyświetla informacje o zużyciu pamięci dla skryptów projektu w czasie rzeczywistym.

    Args:
        project_dir (str): Katalog główny projektu.
        interval (int): Interwał czasowy w sekundach dla aktualizacji.
    """
    try:
        while True:
            os.system('clear')
            processes = get_memory_usage_by_scripts(project_dir)

            if not processes:
                print(f"Brak procesów powiązanych z projektem: {project_dir}")
                time.sleep(interval)
                continue

            total_memory = sum(proc['memory_usage'] for proc in processes)

            print(f"{'PID':<10}{'Nazwa':<20}{'Zużycie pamięci (MB)':<20}{'Linia poleceń':<50}")
            print("-" * 100)
            for proc in processes:
                print(f"{proc['pid']:<10}{proc['name']:<20}{proc['memory_usage'] / (1024 ** 2):<20.2f}{proc['cmdline']:<50}")
            print("-" * 100)
            print(f"{'Razem':<30}{total_memory / (1024 ** 2):<20.2f}{'MB':<50}")

            analyze_memory_objects()

            print(f"\nAktualizacja co {interval} sekund...")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nProgram zatrzymany przez użytkownika.")


if __name__ == "__main__":
    # Używa BASE_DIR z settings.py
    project_directory = str(BASE_DIR)
    print(f"🔍 Zbieranie informacji o zużyciu pamięci dla projektu: {project_directory}")
    display_memory_usage(project_directory, interval=1)
