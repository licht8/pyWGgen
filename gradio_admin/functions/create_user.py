#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

def create_user(username, email="N/A", telegram_id="N/A"):
    if not username:
        return "Error: Username cannot be empty.", None

    # Получаем абсолютные пути
    base_dir = Path(__file__).parent.parent.parent
    config_path = base_dir / "configs" / f"{username}.conf"
    
    # Проверка существования пользователя перед вызовом subprocess
    if config_path.exists():
        return f"Error: User '{username}' already exists!", None

    try:
        # Запускаем процесс с захватом stderr
        result = subprocess.run(
            ["python3", "main.py", username, email, telegram_id],
            check=True,
            cwd=str(base_dir),
            capture_output=True,
            text=True
        )
        
        # Проверяем создание QR-кода
        qr_code_path = base_dir / "user" / "data" / "qrcodes" / f"{username}.png"
        if qr_code_path.exists():
            return f"✅ User {username} successfully created.", str(qr_code_path)
        return f"✅ User {username} created, but QR code not found.", None

    except subprocess.CalledProcessError as e:
        # Обрабатываем ошибки из stderr
        error_msg = e.stderr.strip()
        if "already exists" in error_msg:
            return f"Error: User '{username}' already exists!", None
        return f"Error: {error_msg or 'Unknown error'}", None