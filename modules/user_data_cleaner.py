#!/usr/bin/env python3
# modules/user_data_cleaner.py
# Модуль для выборочной очистки данных пользователей

import os
import shutil
import subprocess
from settings import SERVER_WG_NIC # SERVER_WG_NIC из файла params
from settings import USER_DB_PATH # База данных пользователей
from settings import SERVER_CONFIG_FILE
from settings import SERVER_BACKUP_CONFIG_FILE

WG_USERS_JSON = "logs/wg_users.json"

def confirm_action(message):
    """Подтверждение действия пользователем."""
    while True:
        choice = input(f"{message} (y/n): ").strip().lower()
        if choice in {"y", "n"}:
            return choice == "y"
        print("⚠️ Пожалуйста, введите 'y' для подтверждения или 'n' для отмены.")


def clean_user_data():
    """Выборочная очистка данных пользователей с подтверждением."""
    try:
        # Очистка user_records.json
        if os.path.exists(USER_DB_PATH) and confirm_action("🧹 Очистить файл user_records.json?"):
            os.remove(USER_DB_PATH)
            print(f"✅ {USER_DB_PATH} очищен.")

        # Очистка wg_users.json
        if os.path.exists(WG_USERS_JSON) and confirm_action("🧹 Очистить файл wg_users.json?"):
            os.remove(WG_USERS_JSON)
            print(f"✅ {WG_USERS_JSON} очищен.")

        # Очистка конфигурации WireGuard
        if os.path.exists(SERVER_CONFIG_FILE) and confirm_action("🧹 Очистить файл конфигурации WireGuard (удалить все ### Client и [Peer])?"):
            # Создание резервной копии
            shutil.copy2(SERVER_CONFIG_FILE, SERVER_BACKUP_CONFIG_FILE)
            print(f"✅ Резервная копия создана: {SERVER_BACKUP_CONFIG_FILE}")

            # Очистка конфигурации
            with open(SERVER_CONFIG_FILE, "r") as wg_file:
                lines = wg_file.readlines()

            # Новый контент без блоков ### Client и связанных [Peer]
            cleaned_lines = []
            inside_client_block = False

            for line in lines:
                stripped_line = line.strip()
                if stripped_line.startswith("### Client"):
                    inside_client_block = True
                elif inside_client_block and stripped_line == "":
                    # Конец блока, переключаем флаг
                    inside_client_block = False
                elif not inside_client_block:
                    cleaned_lines.append(line)

            with open(SERVER_CONFIG_FILE, "w") as wg_file:
                wg_file.writelines(cleaned_lines)
            print(f"✅ Конфигурация WireGuard очищена.")

        # Синхронизация WireGuard

        sync_command = f'wg syncconf "{SERVER_WG_NIC}" <(wg-quick strip "{SERVER_WG_NIC}")'
        subprocess.run(sync_command, shell=True, check=True, executable='/bin/bash')
        print(f"WireGuard синхронизирован для интерфейса {SERVER_WG_NIC}")

        print("🎉 Очистка завершена. Все данные обработаны.")

    except Exception as e:
        print(f"❌ Ошибка при очистке данных: {e}")