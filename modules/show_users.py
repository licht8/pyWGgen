#!/usr/bin/env python3
# modules/show_users.py
# Модуль для вывода списка пользователей из user_records.json

import os
import json

USER_RECORDS_JSON = os.path.join("user", "data", "user_records.json")

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
