#!/usr/bin/env python3

"""
get_memory_usage_by_scripts.py
Скрипт для отображения в реальном времени информации о потреблении памяти скриптами проекта wg_qr_generator.
"""

import psutil
import os
import sys
import time
import gc
import tracemalloc
from pathlib import Path
from memory_profiler import memory_usage

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


def display_memory_usage_with_functions(project_dir, interval=1):
    """
    В режиме реального времени отображает информацию о потреблении памяти скриптами проекта
    с использованием tracemalloc и memory-profiler.

    :param project_dir: Путь к корневой директории проекта.
    :param interval: Интервал обновления в секундах.
    """
    tracemalloc.start(25)  # Увеличиваем глубину трассировки
    try:
        while True:
            os.system('clear')
            processes = get_memory_usage_by_scripts(project_dir)

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

            # Разбивка по функциям
            print("\n🔍 Разбивка по функциям:")
            snapshot = tracemalloc.take_snapshot()
            stats = snapshot.statistics('lineno')

            if stats:
                for stat in stats[:10]:
                    size_kb = stat.size / 1024
                    filename = stat.traceback[0].filename
                    line_number = stat.traceback[0].lineno
                    print(f"{size_kb:<15.2f}{filename:<50}{line_number}")
            else:
                print("Нет данных для разбивки по функциям.")

            # Загруженные модули
            print("\n🔍 Загруженные модули:")
            modules = sys.modules
            module_sizes = [(mod, sys.getsizeof(obj)) for mod, obj in modules.items() if hasattr(obj, '__file__')]
            module_sizes = sorted(module_sizes, key=lambda x: x[1], reverse=True)[:10]
            for mod, size in module_sizes:
                print(f"{mod:<50}{size / 1024:.2f} KB")

            # Используемая память
            print("\n🔍 Объекты в памяти:")
            object_types = {}
            for obj in gc.get_objects():
                obj_type = type(obj).__name__
                object_types[obj_type] = object_types.get(obj_type, 0) + sys.getsizeof(obj)
            sorted_objects = sorted(object_types.items(), key=lambda x: x[1], reverse=True)[:10]
            for obj_type, size in sorted_objects:
                print(f"{obj_type:<30}{size / 1024:.2f} KB")

            print(f"\nОбновление каждые {interval} секунд...")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем.")
    finally:
        tracemalloc.stop()


if __name__ == "__main__":
    project_directory = str(BASE_DIR)
    print(f"🔍 Сбор информации о памяти для проекта: {project_directory}")
    display_memory_usage_with_functions(project_directory, interval=1)
