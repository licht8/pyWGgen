#!/usr/bin/env python3
# gradio_admin/functions/format_helpers.py
# Funkcje pomocnicze do formatowania danych w projekcie pyWGgen

from datetime import datetime

def format_time(iso_time):
    """Formatuje czas z ISO 8601 do czytelnego formatu."""
    try:
        dt = datetime.fromisoformat(iso_time)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "N/A"

def calculate_time_remaining(expiry_time):
    """Oblicza pozostały czas do wygaśnięcia."""
    try:
        dt_expiry = datetime.fromisoformat(expiry_time)
        delta = dt_expiry - datetime.now()
        if delta.days >= 0:
            return f"{delta.days} dni"
        return "Wygasło"
    except Exception:
        return "N/A"

def format_user_info(username, user_data, table_row):
    """
    Formatuje informacje o użytkowniku do wyświetlenia w interfejsie.

    :param username: Nazwa użytkownika
    :param user_data: Słownik z informacjami o użytkowniku
    :param table_row: Lista danych wiersza tabeli
    :return: Sformatowany ciąg z informacjami o użytkowniku
    """
    created = user_data.get("created_at", "N/A")
    expires = user_data.get("expires_at", "N/A")
    int_ip = user_data.get("address", "N/A")
    ext_ip = table_row[3] if len(table_row) > 3 else "N/A"
    up = table_row[4] if len(table_row) > 4 else "N/A"
    down = table_row[5] if len(table_row) > 5 else "N/A"
    state = table_row[6] if len(table_row) > 6 else "N/A"

    # Skonstruuj tekstowy wynik
    user_info = f"""
👤 Użytkownik: {username}
📧 Email: [user@mail.wg](mailto:user@mail.wg)
🌱 Utworzony: {format_time(created)}
🔥 Wygaśnie: {format_time(expires)}
🌐 IP wewnętrzne: {int_ip}
🌎 IP zewnętrzne: {ext_ip}
💾 Wysłane: {up}
💽 Odbite: {down}
✅ Status: {state}
"""
    return user_info.strip()
