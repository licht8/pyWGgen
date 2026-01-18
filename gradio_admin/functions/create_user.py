#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

def create_user(username, email="N/A", telegram_id="N/A"):
    """Tworzy nowego użytkownika WireGuard z konfiguracją i kodem QR."""
    if not username:
        return "Błąd: Nazwa użytkownika nie może być pusta.", None

    # Pobierz absolutne ścieżki
    base_dir = Path(__file__).parent.parent.parent
    config_path = base_dir / "configs" / f"{username}.conf"
    
    # Sprawdź istnienie użytkownika przed wywołaniem subprocess
    if config_path.exists():
        return f"Błąd: Użytkownik '{username}' już istnieje!", None

    try:
        # Uruchom proces z przechwyceniem stderr
        result = subprocess.run(
            ["python3", "main.py", username, email, telegram_id],
            check=True,
            cwd=str(base_dir),
            capture_output=True,
            text=True
        )
        
        # Sprawdź utworzenie kodu QR
        qr_code_path = base_dir / "user" / "data" / "qrcodes" / f"{username}.png"
        if qr_code_path.exists():
            return f"✅ Użytkownik {username} pomyślnie utworzony.", str(qr_code_path)
        return f"✅ Użytkownik {username} utworzony, ale kod QR nie znaleziony.", None

    except subprocess.CalledProcessError as e:
        # Obsłuż błędy ze stderr
        error_msg = e.stderr.strip()
        if "already exists" in error_msg:
            return f"Błąd: Użytkownik '{username}' już istnieje!", None
        return f"Błąd: {error_msg or 'Nieznany błąd'}", None
