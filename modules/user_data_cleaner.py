#!/usr/bin/env python3
# modules/user_data_cleaner.py
# Модуль для выборочной очистки данных пользователей

import os
import shutil
import subprocess

USER_DATA_DIR = "user/data"
USER_LOGS_DIR = "logs"
USER_RECORDS_JSON = "user/data/user_records.json"
WG_USERS_JSON = "logs/wg_users.json"
WG_CONFIG_FILE = "/etc/wireguard/wg0.conf"
WG_BACKUP_FILE = "/etc/wireguard/wg0.conf.bak"


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
        if os.path.exists(USER_RECORDS_JSON) and confirm_action("🧹 Очистить файл user_records.json?"):
            os.remove(USER_RECORDS_JSON)
            print(f"✅ {USER_RECORDS_JSON} очищен.")

        # Очистка wg_users.json
        if os.path.exists(WG_USERS_JSON) and confirm_action("🧹 Очистить файл wg_users.json?"):
            os.remove(WG_USERS_JSON)
            print(f"✅ {WG_USERS_JSON} очищен.")

        # Очистка конфигурации WireGuard
        if os.path.exists(WG_CONFIG_FILE) and confirm_action("🧹 Очистить файл конфигурации WireGuard (удалить все [Peer])?"):
            # Создание резервной копии
            shutil.copy2(WG_CONFIG_FILE, WG_BACKUP_FILE)
            print(f"✅ Резервная копия создана: {WG_BACKUP_FILE}")

            # Очистка конфигурации
            with open(WG_CONFIG_FILE, "r") as wg_file:
                lines = wg_file.readlines()

            # Новый контент без блоков [Peer]
            cleaned_lines = []
            inside_peer_block = False

            for line in lines:
                if line.strip().startswith("[Peer]"):
                    inside_peer_block = True
                elif inside_peer_block and line.strip() == "":
                    # Конец блока [Peer], переключаем флаг
                    inside_peer_block = False
                elif not inside_peer_block:
                    cleaned_lines.append(line)

            with open(WG_CONFIG_FILE, "w") as wg_file:
                wg_file.writelines(cleaned_lines)
            print(f"✅ Конфигурация WireGuard очищена.")

        # Перезапуск WireGuard
        if confirm_action("🔄 Перезапустить WireGuard?"):
            result = subprocess.run(["systemctl", "restart", f"wg-quick@{os.path.basename(WG_CONFIG_FILE).replace('.conf', '')}"])
            if result.returncode == 0:
                print("✅ WireGuard успешно перезапущен.")
            else:
                print("❌ Не удалось перезапустить WireGuard.")

        print("🎉 Очистка завершена. Все данные обработаны.")

    except Exception as e:
        print(f"❌ Ошибка при очистке данных: {e}")