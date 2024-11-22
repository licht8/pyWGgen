#!/usr/bin/env python3
# gradio_admin/functions/format_helpers.py
# Вспомогательные функции для форматирования данных в проекте wg_qr_generator


from datetime import datetime

def format_time(iso_time):
    """Форматирует время из ISO 8601 в читаемый формат."""
    try:
        dt = datetime.fromisoformat(iso_time)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "N/A"


def calculate_time_remaining(expiry_time):
    """Вычисляет оставшееся время до истечения."""
    try:
        dt_expiry = datetime.fromisoformat(expiry_time)
        delta = dt_expiry - datetime.now()
        if delta.days >= 0:
            return f"{delta.days} days"
        return "Expired"
    except Exception:
        return "N/A"


def format_user_info(username, user_data, table_row):
    """
    Форматирует информацию о пользователе для отображения в интерфейсе.

    :param username: Имя пользователя
    :param user_data: Словарь с информацией о пользователе
    :param table_row: Список данных строки таблицы
    :return: Отформатированная строка с информацией о пользователе
    """
    created = user_data.get("created_at", "N/A")
    expires = user_data.get("expires_at", "N/A")
    int_ip = user_data.get("address", "N/A")
    ext_ip = table_row[3] if len(table_row) > 3 else "N/A"
    up = table_row[4] if len(table_row) > 4 else "N/A"
    down = table_row[5] if len(table_row) > 5 else "N/A"
    state = table_row[6] if len(table_row) > 6 else "N/A"

    # Формируем текстовый вывод
    user_info = f"""
👤 User: {username}
📧 Email: user@mail.wg
🌱 Created: {format_time(created)}
🔥 Expires: {format_time(expires)}
🌐 Internal IP: {int_ip}
🌎 External IP: {ext_ip}
⬆️ Uploaded: {up}
⬇️ Downloaded: {down}
✅ Status: {state}
"""
    return user_info.strip()
