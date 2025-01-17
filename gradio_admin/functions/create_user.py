#!/usr/bin/env python3
# gradio_admin/functions/create_user.py
# Logic for creating users via main.py

import os
import subprocess

def create_user(username, email="N/A", telegram_id="N/A"):
    if not username:
        return "Error: username cannot be empty.", None

    try:
        subprocess.run(
            ["python3", "main.py", username, email, telegram_id],
            check=True,
            cwd=os.path.abspath(os.path.dirname(__file__) + "/../../")
        )
        qr_code_path = os.path.join("user", "data", "qrcodes", f"{username}.png")
        absolute_path = os.path.abspath(qr_code_path)
        
        if os.path.exists(absolute_path):
            return f"✅ User {username} successfully created.", absolute_path
        return f"✅ User {username} successfully created, but QR code not found.", None

    except subprocess.CalledProcessError as e:
        return f"Error while creating user: {str(e)}", None
