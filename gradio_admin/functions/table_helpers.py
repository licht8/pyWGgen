#!/usr/bin/env python3
# gradio_admin/functions/table_helpers.py
# Утилиты для обработки и отображения таблицы в проекте wg_qr_generator

from gradio_admin.functions.format_helpers import format_time, calculate_time_remaining
from gradio_admin.wg_users_stats import load_data

def update_table(show_inactive):
    """Форматирует данные таблицы для отображения."""
    table = load_data(show_inactive)
    formatted_rows = []

    for row in table:
        username = row[0] if len(row) > 0 else "N/A"
        allowed_ips = row[2] if len(row) > 2 else "N/A"
        endpoint = row[1] if len(row) > 1 else "N/A"
        up = row[4] if len(row) > 4 else "N/A"
        down = row[3] if len(row) > 3 else "N/A"
        status = row[6] if len(row) > 6 else "N/A"
        telegram_id = row[7] if len(row) > 7 else "N/A"
        peer = row[8] if len(row) > 8 else "N/A"
        created = row[9] if len(row) > 9 else "N/A"
        expires = row[10] if len(row) > 10 else "N/A"

        # Эмодзи для состояния
        status_emoji = "🟢" if status == "active" else "🔴"

        # Формирование строк для пользователя
        formatted_rows.append([f"👤 User account : {username}", f"📧 Telegram ID : {telegram_id}"])
        formatted_rows.append([f"🌐 Peer : {peer}", f"📅 Time Left : {calculate_time_remaining(expires)}"])
        formatted_rows.append([f"🌐 Endpoint : {endpoint}", f"⬆️ Uploaded : {up}"])
        formatted_rows.append([f"⬇️ Downloaded : {down}", f"🌐 IP : {allowed_ips}"])
        formatted_rows.append([f"🌱 Created : {format_time(created)}", f"🔥 Expires : {format_time(expires)}"])
        formatted_rows.append([f"State : {status_emoji}", ""])

        # Добавление пустой строки между пользователями
        formatted_rows.append(["", ""])

    return formatted_rows
