#!/usr/bin/env python3

"""
get_memory_usage_by_scripts.py
Скрипт для отображения в реальном времени информации о потреблении памяти скриптами проекта wg_qr_generator.
"""

import psutil
import os
import sys
import time
from pathlib import Path

# Добавляем путь к корневой директории проекта в sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
sys.path.append(str(PROJECT_DIR))

# Импортируем настройки
try:
    from settings import BASE_DIR
except ImportError:
    print("❌ Не удалось найти settings.py. Убедитесь, что файл находится в корневой директории проекта.")
    sys.exit(1)


def get_memory_usage_by_scripts(project_dir):
    """
    Собирает информацию о потреблении памяти скриптами проекта и сортирует по объему потребляемой памяти.

    :param project_dir: Путь к корневой директории проекта.
    :return: Список процессов с информацией об использовании памяти.
    """
    project_dir = os.path.abspath(project_dir)
    processes_info = []

    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline', 'memory_info', 'cwd']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            cmdline = proc.info['cmdline']
            cwd = proc.info.get('cwd')  # Рабочая директория процесса
            memory_usage = proc.info['memory_info'].rss  # Используемая память в байтах

            # Проверяем, относится ли процесс к проекту
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

    # Сортируем процессы по объему используемой памяти
    sorted_processes = sorted(processes_info, key=lambda x: x['memory_usage'], reverse=True)
    return sorted_processes


def display_memory_usage(project_dir, interval=5):
    """
    В режиме реального времени отображает информацию о потреблении памяти скриптами проекта.

    :param project_dir: Путь к корневой директории проекта.
    :param interval: Интервал обновления в секундах.
    """
    try:
        while True:
            processes = get_memory_usage_by_scripts(project_dir)
            os.system('clear')

            if not processes:
                print(f"Нет процессов, связанных с проектом: {project_dir}")
                time.sleep(interval)
                continue

            total_memory = sum(proc['memory_usage'] for proc in processes)

            print(f"{'ID':<10}{'Name':<20}{'Memory Usage (MB)':<20}{'Command Line':<50}")
            print("-" * 100)
            for proc in processes:
                print(f"{proc['pid']:<10}{proc['name']:<20}{proc['memory_usage'] / (1024 ** 2):<20.2f}{proc['cmdline']:<50}")
            
            print("-" * 100)
            print(f"{'Итог':<30}{total_memory / (1024 ** 2):<20.2f}{'MB':<50}")
            print(f"\nОбновление каждые {interval} секунд...")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем.")



if __name__ == "__main__":
    # Используем BASE_DIR из settings.py
    project_directory = str(BASE_DIR)
    print(f"🔍 Сбор информации о памяти для проекта: {project_directory}")
    display_memory_usage(project_directory, interval=5)
