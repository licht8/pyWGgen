#!/usr/bin/env python3
# modules/manage_expiry_menu.py
## Подменю для управления сроками действия VPN аккаунтов WireGuard

import os
import subprocess


def manage_expiry_menu():
    """Подменю для работы с manage_expiry.py."""
    MANAGE_EXPIRY_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../manage_expiry.py"))

    if not os.path.exists(MANAGE_EXPIRY_SCRIPT):
        print(f"❌ Скрипт {MANAGE_EXPIRY_SCRIPT} не найден.")
        return

    while True:
        print("\n========== Управление сроками действия ==========")
        print("1. Проверить, истек ли срок действия аккаунтов")
        print("2. Продлить срок действия аккаунта")
        print("3. Сбросить срок действия аккаунта")
        print("0. Вернуться в главное меню")
        print("=================================================")

        choice = input("Выберите действие: ").strip()
        if choice == "1":
            print("🔍 Проверка сроков действия...")
            subprocess.run(["python3", MANAGE_EXPIRY_SCRIPT, "check"])
        elif choice == "2":
            username = input("Введите имя пользователя для продления срока: ").strip()
            days = input("Введите количество дней для продления: ").strip()
            subprocess.run(["python3", MANAGE_EXPIRY_SCRIPT, "extend", username, "--days", days])
        elif choice == "3":
            username = input("Введите имя пользователя для сброса срока: ").strip()
            subprocess.run(["python3", MANAGE_EXPIRY_SCRIPT, "reset", username])
        elif choice == "0":
            print("🔙 Возврат в главное меню...")
            break
        else:
            print("⚠️ Некорректный выбор. Попробуйте еще раз.")
