#!/usr/bin/env python3

"""
swap_edit.py - Создание и настройка swap с эффектами ИИ.

Этот скрипт поддерживает два режима:
1. Интерактивный режим с эффектами печати (ИИ-стиль).
2. Консольный режим для автоматического выполнения.

Функции:
- Проверка текущего swap.
- Создание нового swap-файла с заданным размером.
- Обновление автозагрузки.

Использование:
- Интерактивный: `sudo python3 swap_edit.py`
- Консольный: `sudo python3 swap_edit.py <размер в MB>`
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from settings import (
    PRINT_SPEED,
    WG_CONFIG_DIR,
    QR_CODE_DIR,
    SERVER_CONFIG_FILE,
    LOG_FILE_PATH,
    LOG_LEVEL,
    DEFAULT_TRIAL_DAYS,
)
from ai_diagnostics.ai_diagnostics import display_message_slowly

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
        display_message_slowly("🚨 Этот скрипт должен быть запущен от имени суперпользователя (root).", indent=False)
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
        display_message_slowly(f"🛠️ Создаю файл подкачки размером {size_mb} MB...")
        run_command(f"dd if=/dev/zero of={swap_file} bs=1M count={size_mb}", check=True)

        # Форматировать файл подкачки
        display_message_slowly("🎨 Форматирую файл подкачки...")
        run_command(f"mkswap {swap_file}", check=True)

        # Активировать файл подкачки
        display_message_slowly("⚡ Активирую файл подкачки...")
        run_command(f"swapon {swap_file}", check=True)

        # Установить права
        display_message_slowly("🔒 Настраиваю права на файл подкачки...")
        run_command(f"chown root:root {swap_file}", check=True)
        run_command(f"chmod 0600 {swap_file}", check=True)

        # Обновить rc.local
        display_message_slowly("📂 Обновляю /etc/rc.local для автозагрузки...")
        rc_local_backup = "/tmp/rc.local.backup"
        if os.path.exists("/etc/rc.local"):
            shutil.copy("/etc/rc.local", rc_local_backup)
        else:
            with open("/etc/rc.local", "w") as rc_local:
                rc_local.write("#!/bin/bash\n")

        with open("/etc/rc.local", "a") as rc_local:
            rc_local.write(f"swapon {swap_file}\n")

        os.chmod("/etc/rc.local", 0o755)

        display_message_slowly(f"✅ Swap-файл создан! Текущий размер: {get_current_swap_size()}")

    except Exception as e:
        display_message_slowly(f"❌ Произошла ошибка: {e}")


def main():
    """Основная функция."""
    check_root()

    # Если передан аргумент размера
    if len(sys.argv) > 1:
        try:
            size_mb = int(sys.argv[1])
            if size_mb > 0:
                display_message_slowly(f"🎯 Автоматический режим: создание swap-файла {size_mb} MB")
                create_swap_file(size_mb)
            else:
                display_message_slowly("⚠️ Размер swap должен быть больше 0.")
                exit(1)
        except ValueError:
            display_message_slowly("⚠️ Передайте корректное число в качестве аргумента.")
            exit(1)
    else:
        # Интерактивный режим
        display_message_slowly(f"🔍 Текущий размер swap: {get_current_swap_size()}")
        try:
            size_mb = int(input("💬 Введите размер нового swap-файла (в MB): "))
            if size_mb > 0:
                create_swap_file(size_mb)
            else:
                display_message_slowly("⚠️ Указан некорректный размер. Операция отменена.")
        except ValueError:
            display_message_slowly("⚠️ Введите корректное число.")


if __name__ == "__main__":
    main()
