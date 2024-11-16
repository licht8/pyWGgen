import os
import json
from datetime import datetime, timedelta
from dateutil import parser # type: ignore
import settings

def load_user_records():
    if os.path.exists(settings.USER_DB_PATH):
        with open(settings.USER_DB_PATH, 'r') as file:
            return json.load(file)
    return {}

def save_user_records(user_data):
    with open(settings.USER_DB_PATH, 'w') as file:
        json.dump(user_data, file, indent=4)

def check_expiry(nickname):
    """
    Проверяет, истек ли срок действия аккаунта пользователя и возвращает оставшееся время.

    Args:
        nickname (str): Имя пользователя для проверки.

    Returns:
        dict: Содержит статус аккаунта и оставшееся время, если аккаунт еще действителен.
    """
    user_data = load_user_records()
    if nickname not in user_data:
        raise ValueError(f"Пользователь {nickname} не найден.")

    expires_at = parser.parse(user_data[nickname]['expires_at'])
    now = datetime.now()

    if now >= expires_at:
        return {"status": "expired", "remaining_time": "Срок действия истек"}

    # Вычисляем оставшееся время
    time_left = expires_at - now
    days_left = time_left.days
    hours_left = time_left.seconds // 3600
    return {
        "status": "active",
        "remaining_time": f"{days_left} дней, {hours_left} часов до окончания"
    }

def extend_expiry(nickname, additional_days):
    """Продлевает срок действия аккаунта пользователя на указанное количество дней."""
    user_data = load_user_records()
    if nickname in user_data:
        expires_at = parser.parse(user_data[nickname]['expires_at'])
        new_expiration_time = expires_at + timedelta(days=additional_days)
        user_data[nickname]['expires_at'] = new_expiration_time.isoformat()
        save_user_records(user_data)
        print(f"Срок действия аккаунта пользователя {nickname} продлен до {new_expiration_time}.")
    else:
        raise ValueError(f"Пользователь {nickname} не найден.")

def reset_expiry(nickname, trial_days=settings.DEFAULT_TRIAL_DAYS):
    """Сбрасывает срок действия аккаунта, начиная отсчет с текущего момента."""
    user_data = load_user_records()
    if nickname in user_data:
        new_expiration_time = datetime.now() + timedelta(days=trial_days)
        user_data[nickname]['expires_at'] = new_expiration_time.isoformat()
        save_user_records(user_data)
        print(f"Срок действия аккаунта пользователя {nickname} сброшен до {new_expiration_time}.")
    else:
        raise ValueError(f"Пользователь {nickname} не найден.")
