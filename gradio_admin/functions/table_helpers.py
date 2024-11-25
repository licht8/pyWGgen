#!/usr/bin/env python3
# gradio_admin/functions/table_helpers.py
# Утилита для обработки и отображения данных в таблице Gradio

from gradio_admin.functions.format_helpers import format_time, calculate_time_remaining
from gradio_admin.wg_users_stats import load_data

def update_table(show_inactive):
    """
    Форматирует данные таблицы с информацией о пользователях WireGuard.
    :param show_inactive: bool, показывать ли неактивных пользователей
    :return: список строк для отображения в таблице
    """
    table = load_data(show_inactive)
    formatted_rows = []

    for user in table:
        if not isinstance(user, dict):  # Проверяем, что user — это словарь
            print(f"⚠️ Ошибка: ожидался словарь, получено: {type(user)}")
            continue

        username = user.get("username", "N/A")
        email = user.get("email", "N/A")
        telegram_id = user.get("telegram_id", "N/A")
        allowed_ips = user.get("allowed_ips", "N/A")
        endpoint = user.get("endpoint", "N/A")
        last_handshake = user.get("last_handshake", "N/A")
        uploaded = user.get("uploaded", "N/A")
        downloaded = user.get("downloaded", "N/A")
        created = user.get("created", "N/A")
        expires = user.get("expiry", "N/A")
        status = user.get("status", "inactive")

        # Определение эмодзи для статуса
        state_emoji = "🟢" if status == "active" else "🔴"

        # Формирование строк для таблицы
        formatted_rows.append([f"👤 User account : {username}", f"📧 User e-mail : {email}"])
        formatted_rows.append([f"📱 Telegram ID : {telegram_id}", f"🌐 Allowed IPs : {allowed_ips}"])
        formatted_rows.append([f"🌎 Endpoint : {endpoint}", f"🤝 Last handshake : {last_handshake}"])
        formatted_rows.append([f"⬆️ Uploaded : {uploaded}", f"⬇️ Downloaded : {downloaded}"])
        formatted_rows.append([f"🌱 Created : {format_time(created)}", f"🔥 Expires : {format_time(expires)}"])
        formatted_rows.append([f"📅 State : {state_emoji}", ""])
        
        # Добавляем разделитель между пользователями
        formatted_rows.append(["", ""])

    return formatted_rows
