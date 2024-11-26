#!/usr/bin/env python3
# create_user.py
## Скрипт для обработки создания пользователей и отображения QR-кодов

import os
import subprocess
import json


def create_user(username):
    """
    Создание нового пользователя и отображение QR-кода.

    :param username: Имя пользователя для WireGuard
    :return: Статус операции и путь к QR-коду (если создан)
    """
    if not username:
        return "Ошибка: имя пользователя не может быть пустым.", None

    # Путь к JSON-файлу с записями пользователей
    user_records_path = os.path.join("user", "data", "user_records.json")

    # Проверка на существование файла записей пользователей
    if os.path.exists(user_records_path):
        with open(user_records_path, "r", encoding="utf-8") as f:
            try:
                user_data = json.load(f)
            except json.JSONDecodeError:
                return "❌ Ошибка чтения файла user_records.json. Проверьте его формат.", None

        # Проверяем, существует ли пользователь
        if username in user_data:
            return f"❌ Пользователь {username} уже существует.", None

    try:
        # Запускаем процесс создания пользователя
        subprocess.run(["python3", "main.py", username], check=True)

        # Формируем путь к QR-коду
        qr_code_path = os.path.join("user", "data", "qrcodes", f"{username}.png")
        absolute_path = os.path.abspath(qr_code_path)

        # Проверяем, создан ли QR-код
        if os.path.exists(absolute_path):
            return f"✅ Пользователь {username} успешно создан.", absolute_path
        else:
            return f"✅ Пользователь {username} успешно создан, но QR-код не найден.", None

    except subprocess.CalledProcessError as e:
        return f"❌ Ошибка при создании пользователя: {str(e)}", None
    except Exception as e:
        return f"❌ Непредвиденная ошибка: {str(e)}", None
