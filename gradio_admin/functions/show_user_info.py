#!/usr/bin/env python3
# gradio_admin/functions/show_user_info.py

from gradio_admin.functions.user_records import load_user_records
from gradio_admin.functions.format_helpers import format_time

def show_user_info(username):
    """Wyświetla szczegółowe informacje o użytkowniku."""
    print(f"[DEBUG] Nazwa użytkownika: {username}")

    # Wczytaj dane z user_records.json
    records = load_user_records()
    user_data = records.get(username)

    if not user_data:
        print(f"[DEBUG] Użytkownik '{username}' nie znaleziony w rekordach.")
        return f"Użytkownik '{username}' nie znaleziony w rekordach."

    # Sformatuj informacje o użytkowniku
    created = user_data.get("created_at", "N/A")
    expires = user_data.get("expires_at", "N/A")
    int_ip = user_data.get("allowed_ips", "N/A")
    total_transfer = user_data.get("total_transfer", "N/A")
    last_handshake = user_data.get("last_handshake", "N/A")
    status = user_data.get("status", "N/A")
    email = user_data.get("email", "N/A")
    subscription_plan = user_data.get("subscription_plan", "N/A")
    total_spent = user_data.get("total_spent", "N/A")
    notes = user_data.get("user_notes", "Brak notatek")

    user_info = f"""
👤 Użytkownik: {username}
📧 Email: {email}
🌱 Utworzony: {format_time(created)}
🔥 Wygaśnie: {format_time(expires)}
🌐 IP wewnętrzne: {int_ip}
📊 Całkowity transfer: {total_transfer}
🤝 Ostatni handshake: {last_handshake}
⚡ Status: {status}
📜 Plan subskrypcji: {subscription_plan}
💳 Wydane łącznie: {total_spent}
📝 Notatki: {notes}
"""
    print(f"[DEBUG] Informacje o użytkowniku:\n{user_info}")
    return user_info.strip()
