#!/usr/bin/env python3
# modules/manage_expiry_menu.py
# Меню для управления сроками действия пользователей WireGuard

import os
import subprocess


def manage_expiry_menu():
    """Меню для управления сроками действия пользователей."""
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
            # Показать всех пользователей
            try:
                subprocess.run(["python3", "modules/manage_expiry.py", "show"])
            except FileNotFoundError:
                print("❌ Скрипт 'manage_expiry.py' не найден.")
            except subprocess.CalledProcessError as e:
                print(f"❌ Ошибка выполнения команды: {e}")

        elif choice == "2":
            # Проверить срок действия аккаунта
            nickname = input("Введите имя пользователя для проверки: ").strip()
            if nickname:
                try:
                    subprocess.run(["python3", "modules/manage_expiry.py", "check", nickname])
                except FileNotFoundError:
                    print("❌ Скрипт 'manage_expiry.py' не найден.")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Ошибка выполнения команды: {e}")
            else:
                print("⚠️ Имя пользователя не может быть пустым.")

        elif choice == "3":
            # Продлить срок действия аккаунта
            nickname = input("Введите имя пользователя для продления срока: ").strip()
            days = input("Введите количество дней для продления: ").strip()
            if nickname and days.isdigit():
                try:
                    subprocess.run(["python3", "modules/manage_expiry.py", "extend", nickname, days])
                except FileNotFoundError:
                    print("❌ Скрипт 'manage_expiry.py' не найден.")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Ошибка выполнения команды: {e}")
            else:
                print("⚠️ Убедитесь, что введены корректные данные.")

        elif choice == "4":
            # Сбросить срок действия аккаунта
            nickname = input("Введите имя пользователя для сброса срока: ").strip()
            days = input("Введите новый срок действия в днях (по умолчанию 30): ").strip() or "30"
            if nickname and days.isdigit():
                try:
                    subprocess.run(["python3", "modules/manage_expiry.py", "reset", nickname, "--days", days])
                except FileNotFoundError:
                    print("❌ Скрипт 'manage_expiry.py' не найден.")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Ошибка выполнения команды: {e}")
            else:
                print("⚠️ Убедитесь, что введены корректные данные.")

        elif choice == "0":
            # Вернуться в главное меню
            print("🔙 Возврат в главное меню...")
            break

        else:
            print("⚠️ Некорректный выбор. Попробуйте еще раз.")
