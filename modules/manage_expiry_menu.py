#!/usr/bin/env python3
# modules/manage_expiry_menu.py
# Меню управления сроками действия пользователей WireGuard

import subprocess
import os
import json

# Пути к скриптам
MANAGE_EXPIRY_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "manage_expiry.py"))
USER_RECORDS_JSON = os.path.abspath(os.path.join(os.path.dirname(__file__), "../user/data/user_records.json"))


def show_all_users():
    """Выводит список всех пользователей из user_records.json."""
    if not os.path.exists(USER_RECORDS_JSON):
        print("❌ Файл user_records.json не найден.")
        return

    try:
        with open(USER_RECORDS_JSON, "r") as file:
            users = json.load(file)
            if not users:
                print("🔍 Пользователи не найдены.")
                return

            print("\n========== Список пользователей ==========")
            for nickname, details in users.items():
                print(f"👤 {nickname}")
            print("==========================================")
    except json.JSONDecodeError:
        print("❌ Ошибка чтения user_records.json.")
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")


def manage_expiry_menu():
    """Меню управления сроками действия."""
    while True:
        print("\n========== Управление сроками действия ==========")
        print("1. Показать всех пользователей")
        print("2. Проверить, истек ли срок действия аккаунтов")
        print("3. Продлить срок действия аккаунта")
        print("4. Сбросить срок действия аккаунта")
        print("0. Вернуться в главное меню")
        print("=================================================")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_all_users()
        elif choice == "2":
            nickname = input("Введите имя пользователя для проверки: ").strip()
            if nickname:
                print("🔍 Проверка сроков действия...")
                subprocess.run(["python3", MANAGE_EXPIRY_SCRIPT, "check", nickname])
        elif choice == "3":
            nickname = input("Введите имя пользователя для продления срока: ").strip()
            if nickname:
                try:
                    days = int(input("Введите количество дней для продления: ").strip())
                    print("⏳ Продление срока действия...")
                    subprocess.run(["python3", MANAGE_EXPIRY_SCRIPT, "extend", nickname, str(days)])
                except ValueError:
                    print("❌ Некорректное значение для дней.")
        elif choice == "4":
            nickname = input("Введите имя пользователя для сброса срока: ").strip()
            if nickname:
                try:
                    days = int(input("Введите новый срок действия в днях (по умолчанию 30): ").strip())
                    print("🔄 Сброс срока действия...")
                    subprocess.run(["python3", MANAGE_EXPIRY_SCRIPT, "reset", nickname, "--days", str(days)])
                except ValueError:
                    print("❌ Некорректное значение для дней.")
        elif choice in {"0", "q"}:
            print("🔙 Возврат в главное меню...")
            break
        else:
            print("⚠️ Некорректный выбор. Попробуйте еще раз.")


if __name__ == "__main__":
    manage_expiry_menu()
