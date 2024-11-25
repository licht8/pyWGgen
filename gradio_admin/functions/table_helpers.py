#!/usr/bin/env python3
# gradio_admin/functions/table_helpers.py
# Форматирование таблицы для Gradio интерфейса

from gradio_admin.wg_users_stats import load_data

def update_table(show_inactive):
    """Обновление таблицы пользователей."""
    table_data = load_data(show_inactive)
    formatted_table = []

    for user in table_data:
        username = user.get("username", "N/A")
        peer = user.get("peer", "N/A")
        telegram_id = user.get("telegram_id", "N/A")
        allowed_ips = user.get("allowed_ips", "N/A")
        status = user.get("status", "inactive")
        status_color = "green" if status == "active" else "red"

        formatted_table.append([
            f"👤 {username}",
            f"📱 {telegram_id}",
            f"🔑 {peer}",
            f"🌐 {allowed_ips}",
            f"<span style='color: {status_color}'>{status}</span>"
        ])

    return formatted_table
