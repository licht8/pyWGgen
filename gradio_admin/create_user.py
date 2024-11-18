#!/usr/bin/env python3
# create_user.py
## Скрипт для обработки создания пользователей и отображения QR-кодов

import os
import subprocess

def create_user(username):
    """Создание нового пользователя и отображение QR-кода."""
    if not username:
        return "Ошибка: имя пользователя не может быть пустым."
    
    try:
        # Запускаем процесс создания пользователя
        subprocess.run(["python3", "main.py", username], check=True)
        
        # Путь к QR-коду
        qr_code_path = os.path.join("user", "data", "qrcodes", f"{username}.png")
        if os.path.exists(qr_code_path):
            return f"✅ Пользователь {username} успешно создан.", qr_code_path
        else:
            return f"✅ Пользователь {username} успешно создан, но QR-код не найден.", None
    except Exception as e:
        return f"❌ Ошибка при создании пользователя: {str(e)}", None
