#!/usr/bin/env python3
# modules/show_users.py
# Модуль для отображения списка пользователей

import os
import json
from datetime import datetime

# Пути к данным
USER_RECORDS_JSON = os.path.join("user", "data", "user_records.json")


def load_json(filepath):
    """Загружает данные из JSON-файла."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def calculate_time_left(expiry_date):
    """
    Вычисляет оставшееся время до истечения срока действия аккаунта.
    :param expiry_date: Дата истечения в формате ISO 8601.
    :return: Оставшееся время в днях или "N/A".
    """
    if expiry_date == "N/A":
        return "N/A"
    try:
        expiry = datetime.fromisoformat(expiry_date)
        now = datetime.now()
        remaining = expiry - now
        return f"{remaining.days} days" if remaining.days > 0 else "Expired"
    except ValueError:
        return "N/A"


def show_all_users():
    """
    Отображает всех пользователей из JSON.
    """
    user_data = load_json(USER_RECORDS_JSON)

    if not user_data:
        print("🔍 Пользователи не найдены.")
        return

    print("========== Список пользователей ==========")
    for username, details in user_data.items():
        print(f"👤 User account : {details.get('username', 'N/A')}")
        print(f"📧 User e-mail : {details.get('email', 'N/A')}")
        print(f"📱 Telegram ID  : {details.get('telegram_id', 'N/A')}")
        print(f"🌱 Created : {details.get('created_at', 'N/A')}")
        print(f"🔥 Expires : {details.get('expires_at', 'N/A')}")
        print(f"🌐 intIP 🟢  : {details.get('allowed_ips', 'N/A')}")
        print(f"⬆️ up : {details.get('uploaded', 'N/A')}")
        print(f"🌎 extIP 🟢  : {details.get('endpoint', 'N/A')}")
        print(f"⬇️ dw : {details.get('downloaded', 'N/A')}")
        print(f"📅 TimeLeft : {calculate_time_left(details.get('expires_at'))}")
        print(f"State : {'✅' if details.get('status', 'inactive') == 'active' else '❌'}\n")

    print("==========================================")


if __name__ == "__main__":
    show_all_users()
