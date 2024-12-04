import tracemalloc
import os
import sys
import time
import psutil
from pathlib import Path

# Настройка путей
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
sys.path.append(str(PROJECT_DIR))

# Импорт настроек
try:
    from settings import BASE_DIR
except ImportError:
    print("❌ Не удалось найти settings.py. Убедитесь, что файл находится в корневой директории проекта.")
    sys.exit(1)

def get_memory_usage_by_scripts(project_dir):
    project_dir = os.path.abspath(project_dir)
    processes_info = []

    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline', 'memory_info', 'cwd']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            cmdline = proc.info['cmdline']
            cwd = proc.info.get('cwd')  # Рабочая директория процесса
            memory_usage = proc.info['memory_info'].rss  # Используемая память в байтах

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

    return sorted(processes_info, key=lambda x: x['memory_usage'], reverse=True)


def display_memory_usage_with_functions(project_dir, interval=1):
    tracemalloc.start()
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
            stats = snapshot.filter_traces((
                tracemalloc.Filter(True, str(BASE_DIR)),
            )).statistics('lineno')

            if stats:
                for stat in stats[:10]:
                    print(f"{stat.traceback.format()}: {stat.size / 1024:.2f} KB")
            else:
                print("Нет данных для разбивки по функциям.")

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
