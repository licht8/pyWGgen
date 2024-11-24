#!/usr/bin/env python3
# modules/manage_expiry_menu.py
## Подменю для управления сроками действия пользователей WireGuard

import subprocess

def manage_expiry_menu():
    """Подменю для работы с manage_expiry.py."""
    while True:
        print("\n========== Управление сроками действия ==========")
        print("1. Проверить, истек ли срок действия аккаунтов")
        print("2. Продлить срок действия аккаунта")
        print("3. Сбросить срок действия аккаунта")
        print("0. Вернуться в главное меню")
        print("=================================================")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            nickname = input("Введите имя пользователя для проверки: ").strip()
            if not nickname:
                print("⚠️ Имя пользователя не указано. Попробуйте снова.")
                continue
            print("🔍 Проверка сроков действия...")
            try:
                subprocess.run(["python3", "modules/manage_expiry.py", "check", nickname], check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Ошибка: {e}")
        elif choice == "2":
            nickname = input("Введите имя пользователя для продления срока: ").strip()
            if not nickname:
                print("⚠️ Имя пользователя не указано. Попробуйте снова.")
                continue
            try:
                days = int(input("Введите количество дней для продления: ").strip())
                print(f"⏳ Продление срока действия пользователя {nickname} на {days} дней...")
                subprocess.run(["python3", "modules/manage_expiry.py", "extend", nickname, "--days", str(days)], check=True)
            except ValueError:
                print("⚠️ Введите корректное число дней.")
            except subprocess.CalledProcessError as e:
                print(f"❌ Ошибка: {e}")
        elif choice == "3":
            nickname = input("Введите имя пользователя для сброса срока: ").strip()
            if not nickname:
                print("⚠️ Имя пользователя не указано. Попробуйте снова.")
                continue
            print(f"🔄 Сброс срока действия пользователя {nickname}...")
            try:
                subprocess.run(["python3", "modules/manage_expiry.py", "reset", nickname], check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Ошибка: {e}")
        elif choice == "0":
            print("🔙 Возврат в главное меню...")
            break
        else:
            print("⚠️ Некорректный выбор. Попробуйте снова.")
