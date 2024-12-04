#!/usr/bin/env python3

"""
get_memory_usage_by_scripts.py
Скрипт для отображения в реальном времени информации о потреблении памяти скриптами проекта wg_qr_generator.
"""

import os
import sys
import time
import tracemalloc
from settings import BASE_DIR


def get_detailed_memory_usage_by_functions():
    """
    Возвращает подробное использование памяти с разбивкой по функциям.
    """
    tracemalloc.start()

    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    detailed_memory = []
    for stat in top_stats[:10]:  # Топ-10 потребителей памяти
        detailed_memory.append({
            "filename": stat.traceback[0].filename,
            "lineno": stat.traceback[0].lineno,
            "size": stat.size / 1024,  # В КБ
            "count": stat.count
        })

    tracemalloc.stop()
    return detailed_memory


def display_detailed_memory_usage(interval=5):
    """
    В режиме реального времени отображает подробную информацию о потреблении памяти с разбивкой по функциям.

    :param interval: Интервал обновления в секундах.
    """
    try:
        while True:
            os.system('clear')
            detailed_memory = get_detailed_memory_usage_by_functions()

            if not detailed_memory:
                print("Нет данных о потреблении памяти.")
                time.sleep(interval)
                continue

            print(f"{'Файл':<40}{'Строка':<10}{'Размер (KB)':<15}{'Кол-во вызовов':<15}")
            print("-" * 80)
            for item in detailed_memory:
                print(f"{item['filename']:<40}{item['lineno']:<10}{item['size']:<15.2f}{item['count']:<15}")

            total_memory = sum(item['size'] for item in detailed_memory)
            print("-" * 80)
            print(f"{'Итог':<40}{'':<10}{total_memory:<15.2f}{'KB':<15}")

            print(f"\nОбновление каждые {interval} секунд...")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем.")


if __name__ == "__main__":
    print(f"🔍 Запущен анализ памяти для проекта: {BASE_DIR}")
    display_detailed_memory_usage()

