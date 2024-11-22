#!/usr/bin/env python3
# gradio_admin/functions/show_user_info.py
# Функции для отображения информации о пользователе в проекте wg_qr_generator

from gradio_admin.functions.user_records import load_user_records
from gradio_admin.functions.format_helpers import format_time

def show_user_info(selected_data, query):
    """Показывает подробную информацию о выбранном пользователе."""
    print("[DEBUG] Вызов функции show_user_info")  # Отладка
    print(f"[DEBUG] Query: {query}")  # Отладка

    if not query.strip():
        return "Please enter a query to filter user data and then click a cell to view user details and perform actions."

    if selected_data is None or len(selected_data) == 0:
        return "Select a row from the table!"

    try:
        row = selected_data if isinstance(selected_data, list) else selected_data.iloc[0].values
        username = row[0].replace("👤 User account : ", "") if len(row) > 0 else "N/A"
        records = load_user_records()
        user_data = records.get(username, {})

        created = user_data.get("created_at", "N/A")
        expires = user_data.get("expires_at", "N/A")
        int_ip = user_data.get("address", "N/A")

        user_info = f"""
👤 User: {username}
📧 Email: user@mail.wg
🌱 Created: {format_time(created)}
🔥 Expires: {format_time(expires)}
🌐 Internal IP: {int_ip}
"""
        print(f"[DEBUG] User info:\n{user_info}")  # Отладка
        return user_info.strip()
    except Exception as e:
        print(f"[DEBUG] Error: {e}")  # Отладка
        return f"Error processing data: {str(e)}"
