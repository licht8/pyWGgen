import psutil
import os

def get_memory_usage_by_scripts(project_dir):
    """
    Собирает информацию о потреблении памяти скриптами проекта и сортирует по объему потребляемой памяти.

    :param project_dir: Путь к корневой директории проекта.
    :return: Список процессов с информацией об использовании памяти.
    """
    project_dir = os.path.abspath(project_dir)
    processes_info = []

    print(f"\n🔍 Проверяем процессы Python, связанные с проектом: {project_dir}")
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline', 'memory_info']):
        try:
            # Извлекаем информацию о процессе
            pid = proc.info['pid']
            name = proc.info['name']
            cmdline = proc.info['cmdline']
            memory_usage = proc.info['memory_info'].rss  # Используемая память в байтах

            # Отладочный вывод для всех процессов Python
            if 'python' in (name or '').lower():
                print(f"  Процесс PID={pid}, name={name}, cmdline={cmdline}")

            # Проверяем, относится ли процесс к нашему проекту
            if cmdline and any(project_dir in arg for arg in cmdline):
                processes_info.append({
                    'pid': pid,
                    'name': name,
                    'cmdline': ' '.join(cmdline),
                    'memory_usage': memory_usage,
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Игнорируем процессы, к которым нет доступа или которые завершились
            continue

    # Сортируем процессы по объему используемой памяти
    sorted_processes = sorted(processes_info, key=lambda x: x['memory_usage'], reverse=True)

    return sorted_processes


def display_memory_usage(project_dir):
    """
    Выводит информацию о потреблении памяти скриптами проекта.

    :param project_dir: Путь к корневой директории проекта.
    """
    processes = get_memory_usage_by_scripts(project_dir)

    if not processes:
        print(f"Нет процессов, связанных с проектом: {project_dir}")
        return

    print(f"{'PID':<10}{'Name':<20}{'Memory Usage (MB)':<20}{'Command Line':<50}")
    print("-" * 100)
    for proc in processes:
        print(f"{proc['pid']:<10}{proc['name']:<20}{proc['memory_usage'] / (1024 ** 2):<20.2f}{proc['cmdline']:<50}")


# Пример использования
if __name__ == "__main__":
    project_directory = "/root/pyWGgen/wg_qr_generator"  # Замените на путь к вашему проекту
    display_memory_usage(project_directory)
