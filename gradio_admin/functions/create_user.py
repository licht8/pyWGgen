#!/usr/bin/env python3
# gradio_admin/functions/create_user.py
# Логика создания пользователей через main.py

import os
import subprocess

def create_user(username, email="N/A", telegram_id="N/A"):
    if not username:
        return "Ошибка: имя пользователя не может быть пустым.", None

    try:
        subprocess.run(
            ["python3", "main.py", username, email, telegram_id],
            check=True,
            cwd=os.path.abspath(os.path.dirname(__file__) + "/../../")
        )
        qr_code_path = os.path.join("user", "data", "qrcodes", f"{username}.png")
        absolute_path = os.path.abspath(qr_code_path)
        
        # Добавьте команду синхронизации WireGuard
        sync_command = 'wg syncconf "wg0" <(wg-quick strip "wg0")'
        subprocess.run(sync_command, shell=True, check=True, executable='/bin/bash')
        
        if os.path.exists(absolute_path):
            return f"✅ Пользователь {username} успешно создан.", absolute_path
        return f"✅ Пользователь {username} успешно создан, но QR-код не найден.", None

    except subprocess.CalledProcessError as e:
        return f"Ошибка при создании пользователя: {str(e)}", None
