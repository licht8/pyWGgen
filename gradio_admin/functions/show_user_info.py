#!/usr/bin/env python3
# gradio_admin/functions/show_user_info.py

from gradio_admin.functions.user_records import load_user_records
from gradio_admin.functions.format_helpers import format_time

def show_user_info(username):
    """Displays detailed information about a user."""
    print(f"[DEBUG] Username: {username}")

    # Load data from user_records.json
    records = load_user_records()
    user_data = records.get(username)

    if not user_data:
        print(f"[DEBUG] User '{username}' not found in records.")
        return f"User '{username}' not found in records."

    # Format user information
    created = user_data.get("created_at", "N/A")
    expires = user_data.get("expires_at", "N/A")
    int_ip = user_data.get("allowed_ips", "N/A")
    total_transfer = user_data.get("total_transfer", "N/A")
    last_handshake = user_data.get("last_handshake", "N/A")
    status = user_data.get("status", "N/A")
    email = user_data.get("email", "N/A")
    subscription_plan = user_data.get("subscription_plan", "N/A")
    total_spent = user_data.get("total_spent", "N/A")
    notes = user_data.get("user_notes", "No notes provided")

    user_info = f"""
👤 User: {username}
📧 Email: {email}
🌱 Created: {format_time(created)}
🔥 Expires: {format_time(expires)}
🌐 Internal IP: {int_ip}
📊 Total Transfer: {total_transfer}
🤝 Last Handshake: {last_handshake}
⚡ Status: {status}
📜 Subscription Plan: {subscription_plan}
💳 Total Spent: {total_spent}
📝 Notes: {notes}
"""
    print(f"[DEBUG] User info:\n{user_info}")
    return user_info.strip()
