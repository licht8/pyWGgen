#!/usr/bin/env python3
# modules/manage_expiry_menu.py
# Меню для управления сроками действия VPN аккаунтов WireGuard

import os
import sys
from modules.account_expiry import check_expiry, extend_expiry, reset_expiry
from modules.show_users import show_all_users

# Добавляем текущий и родительский каталог в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
            result = check_expiry(nickname)
            print(result)
        elif choice == "3":
            nickname = input("Введите имя пользователя для продления срока: ").strip()
            days = input("Введите количество дней для продления: ").strip()
            extend_expiry(nickname, int(days))
        elif choice == "4":
            nickname = input("Введите имя пользователя для сброса срока: ").strip()
            reset_expiry(nickname)
        elif choice in ["0", "q"]:
            print("🔙 Возврат в главное меню...")
            break
        else:
            print("⚠️ Некорректный выбор. Попробуйте еще раз.")

if __name__ == "__main__":
    manage_expiry_menu()
