#!/usr/bin/env python3

"""
swap_edit.py - Создание и настройка swap с улучшенным выводом и корректным управлением существующим swap.

Особенности:
1. Автоматическое отключение и удаление существующего файла подкачки.
2. Красивый форматированный вывод для удобства.
3. Поддержка интерактивного и консольного режимов.
4. Табличное представление данных (до и после изменений).
5. Возможность вызова как модуля из других скриптов.

Использование:
- Интерактивный: `sudo python3 swap_edit.py`
- Консольный: `sudo python3 swap_edit.py <размер в MB>`
"""

import os
import sys
import time
import subprocess
import shutil
import signal
from pathlib import Path
from prettytable import PrettyTable

# Добавляем корневую директорию проекта в sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
sys.path.append(str(PROJECT_DIR))

# Импорт модулей проекта
from settings import PRINT_SPEED, LINE_DELAY
from ai_diagnostics.ai_diagnostics import display_message_slowly


def run_command(command, check=True):
    """Выполнить команду в терминале и вернуть вывод."""
    try:
        result = subprocess.run(
            command, shell=True, text=True, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Ошибка: {e.stderr.strip()}")
        return None


def check_root():
    """Проверить, запущен ли скрипт от имени root."""
    if os.geteuid() != 0:
        display_message_slowly("🚨 Этот скрипт должен быть запущен от имени суперпользователя (root).", indent=False)
        exit(1)


def get_swap_info():
    """Получить информацию о swap и памяти."""
    output = run_command("free -h | grep -E 'Swap|Mem'")
    table = PrettyTable(["Тип", "Общий", "Использовано", "Свободно"])
    for line in output.split("\n"):
        if line:
            parts = line.split()
            table.add_row([parts[0], parts[1], parts[2], parts[3]])
    return table


def disable_existing_swap(swap_file="/swap"):
    """Отключить и удалить существующий файл подкачки, если он используется."""
    if os.path.exists(swap_file):
        display_message_slowly(f"   🔍 Обнаружен существующий swap-файл: {swap_file}")
        run_command(f"swapoff {swap_file}", check=False)
        try:
            os.remove(swap_file)
            display_message_slowly(f"   🗑️ Удален существующий swap-файл: {swap_file}")
        except Exception as e:
            display_message_slowly(f"   ❌ Не удалось удалить файл: {e}")


def create_swap_file(size_mb):
    """Создать и активировать файл подкачки."""
    try:
        swap_file = "/swap"

        # Отключить и удалить существующий swap
        disable_existing_swap(swap_file)

        # Создать файл подкачки
        display_message_slowly(f"   🛠️ Создаю файл подкачки размером {size_mb} MB...")
        run_command(f"dd if=/dev/zero of={swap_file} bs=1M count={size_mb}", check=True)

        # Форматировать файл подкачки
        display_message_slowly("   🎨 Форматирую файл подкачки...")
        run_command(f"mkswap {swap_file}", check=True)

        # Активировать файл подкачки
        display_message_slowly("   ⚡ Активирую файл подкачки...")
        run_command(f"swapon {swap_file}", check=True)

        # Установить права
        display_message_slowly("   🔒 Настраиваю права на файл подкачки...")
        run_command(f"chown root:root {swap_file}", check=True)
        run_command(f"chmod 0600 {swap_file}", check=True)

        # Обновить rc.local
        display_message_slowly("   📂 Обновляю /etc/rc.local для автозагрузки...")
        rc_local_backup = "/tmp/rc.local.backup"
        if os.path.exists("/etc/rc.local"):
            shutil.copy("/etc/rc.local", rc_local_backup)
        else:
            with open("/etc/rc.local", "w") as rc_local:
                rc_local.write("#!/bin/bash\n")

        with open("/etc/rc.local", "a") as rc_local:
            rc_local.write(f"swapon {swap_file}\n")

        os.chmod("/etc/rc.local", 0o755)

        display_message_slowly(f"   ✅ Swap-файл создан и активирован. Размер: {size_mb} MB")

    except Exception as e:
        display_message_slowly(f"   ❌ Произошла ошибка: {e}")


def safe_exit(signal_received, frame):
    """Корректное завершение работы."""
    display_message_slowly("\n⚠️ Завершение работы. Если вы настраивали swap, проверьте состояние вручную.")
    sys.exit(0)


def swap_edit(size_mb=None):
    """Основная функция настройки swap."""
    # Установить обработчик Ctrl+C
    signal.signal(signal.SIGINT, safe_exit)

    # Проверить привилегии root
    check_root()

    # Показать информацию перед изменениями
    display_message_slowly("📊 Состояние памяти перед изменениями:")
    print(get_swap_info())

    if size_mb:
        # Автоматический режим
        create_swap_file(size_mb)
    else:
        # Интерактивный режим
        try:
            size_mb = int(input("💬 Введите размер нового swap-файла (в MB): "))
            if size_mb > 0:
                create_swap_file(size_mb)
            else:
                display_message_slowly("⚠️ Указан некорректный размер. Операция отменена.")
        except ValueError:
            display_message_slowly("⚠️ Введите корректное число.")
            return

    # Показать информацию после изменений
    display_message_slowly("📊 Состояние памяти после изменений:")
    print(get_swap_info())


if __name__ == "__main__":
    # Определяем, запущен ли скрипт напрямую или вызван как модуль
    if len(sys.argv) > 1:
        try:
            size_mb = int(sys.argv[1])
            swap_edit(size_mb)
        except ValueError:
            display_message_slowly("⚠️ Передайте корректное число в качестве аргумента.")
    else:
        swap_edit()
