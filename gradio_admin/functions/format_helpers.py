#!/usr/bin/env python3
# gradio_admin/functions/format_helpers.py
# Helper functions for formatting data in the wg_qr_generator project

from datetime import datetime

def format_time(iso_time):
    """Formats time from ISO 8601 to a readable format."""
    try:
        dt = datetime.fromisoformat(iso_time)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "N/A"

def calculate_time_remaining(expiry_time):
    """Calculates the remaining time until expiration."""
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
    Formats user information for display in the interface.

    :param username: Username
    :param user_data: Dictionary containing user information
    :param table_row: List of table row data
    :return: Formatted string with user information
    """
    created = user_data.get("created_at", "N/A")
    expires = user_data.get("expires_at", "N/A")
    int_ip = user_data.get("address", "N/A")
    ext_ip = table_row[3] if len(table_row) > 3 else "N/A"
    up = table_row[4] if len(table_row) > 4 else "N/A"
    down = table_row[5] if len(table_row) > 5 else "N/A"
    state = table_row[6] if len(table_row) > 6 else "N/A"

    # Construct the textual output
    user_info = f"""
👤 User: {username}
📧 Email: user@mail.wg
🌱 Created: {format_time(created)}
🔥 Expires: {format_time(expires)}
🌐 Internal IP: {int_ip}
🌎 External IP: {ext_ip}
💾 Uploaded: {up}
💽 Downloaded: {down}
✅ Status: {state}
"""
    return user_info.strip()
