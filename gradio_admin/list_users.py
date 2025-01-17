#!/usr/bin/env python3
# list_users.py
# Script to display a list of users with expiration and IP address information.

import os
import json
from datetime import datetime
from modules.utils import read_json

USER_RECORDS_PATH = os.path.join("user", "data", "user_records.json")

def list_users():
    """
    Read the list of users and display their information.
    :return: List of users or an error message.
    """
    if not os.path.exists(USER_RECORDS_PATH):
        return "❌ File user_records.json not found."

    try:
        user_data = read_json(USER_RECORDS_PATH)
        if not user_data:
            return "❌ No registered users."

        users_list = []
        for username, details in user_data.items():
            created_at = details.get("created_at", "N/A")
            expires_at = details.get("expires_at", "N/A")
            address = details.get("address", "N/A")

            # Calculate remaining time
            try:
                expires_datetime = datetime.fromisoformat(expires_at)
                remaining_time = expires_datetime - datetime.now()
                remaining_days = remaining_time.days
                remaining_str = f"{remaining_days} days" if remaining_days > 0 else "Expired"
            except Exception:
                remaining_str = "Error in expiration data"

            user_info = (
                f"👤 User: {username}\n"
                f"   📅 Created: {created_at}\n"
                f"   ⏳ Expires: {expires_at}\n"
                f"   ⏳ Remaining: {remaining_str}\n"
                f"   🌐 Address: {address}"
            )
            users_list.append(user_info)

        return "\n\n".join(users_list)

    except json.JSONDecodeError:
        return "❌ Error reading user_records.json. Check its format."
    except Exception as e:
        return f"❌ Error: {str(e)}"
