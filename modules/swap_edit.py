#!/usr/bin/env python3

"""
swap_edit.py - Скрипт для создания и настройки файла подкачки (swap) в CentOS Stream 8 и выше.

Этот скрипт предназначен для автоматической настройки файла подкачки:
1. Проверяет текущий объем swap.
2. Позволяет задать новый размер swap-файла в мегабайтах.
3. Создает swap-файл, форматирует его и активирует без перезагрузки системы.
4. Обновляет /etc/rc.local для автоматической активации swap при перезагрузке.

Требования:
- Запуск от имени суперпользователя (root).
- Совместим с CentOS Stream 8 и выше.

Использование:
1. Запустите скрипт от имени root: `sudo python3 swap_edit.py`
2. Укажите размер swap-файла в мегабайтах, следуя инструкциям.

Результат:
- Новый swap-файл будет создан и активирован.
- /etc/rc.local будет обновлен для автоматической активации swap.

Автор: WireGuard.TOP
Дата: 2024
"""

import os
import subprocess
import shutil


def run_command(command, check=True):
    """Выполнить команду в терминале и вернуть вывод."""
    try:
        result = subprocess.run(
            command, shell=True, text=True, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Ошибка: {e.stderr.strip()}")
        return None


def check_root():
    """Проверить, запущен ли скрипт от имени root."""
    if os.geteuid() != 0:
        print("Этот скрипт необходимо запускать от имени суперпользователя (root).")
        exit(1)


def get_current_swap_size():
    """Получить текущий размер swap."""
    output = run_command("free -h | awk '/^Swap:/ {print $2}'")
    return output if output else "0 GB"


def create_swap_file(size_mb):
    """Создать и активировать файл подкачки."""
    try:
        swap_file = "/swap"

        # Отключить текущий swap
        run_command("swapoff -a", check=False)

        # Создать файл подкачки
        print(f"Создаю файл подкачки размером {size_mb} MB...")
        run_command(f"dd if=/dev/zero of={swap_file} bs=1M count={size_mb}", check=True)

        # Форматировать файл подкачки
        print("Форматирую файл подкачки...")
        run_command(f"mkswap {swap_file}", check=True)

        # Активировать файл подкачки
        print("Активирую файл подкачки...")
        run_command(f"swapon {swap_file}", check=True)

        # Установить права
        print("Настраиваю права на файл подкачки...")
        run_command(f"chown root:root {swap_file}", check=True)
        run_command(f"chmod 0600 {swap_file}", check=True)

        # Обновить rc.local
        print("Обновляю /etc/rc.local для автоматической активации swap...")
        rc_local_backup = "/tmp/rc.local.backup"
        if os.path.exists("/etc/rc.local"):
            shutil.copy("/etc/rc.local", rc_local_backup)
        else:
            with open("/etc/rc.local", "w") as rc_local:
                rc_local.write("#!/bin/bash\n")

        with open("/etc/rc.local", "a") as rc_local:
            rc_local.write(f"swapon {swap_file}\n")

        os.chmod("/etc/rc.local", 0o755)

        print(f"Swap-файл успешно создан! Текущий размер swap: {get_current_swap_size()}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")


def main():
    """Основная функция."""
    check_root()
    print(f"Текущий размер swap: {get_current_swap_size()}")
    try:
        size_mb = int(input("Введите размер нового swap-файла (в MB): "))
        if size_mb > 0:
            create_swap_file(size_mb)
        else:
            print("Указан некорректный размер. Операция отменена.")
    except ValueError:
        print("Введите корректное число.")


if __name__ == "__main__":
    main()
