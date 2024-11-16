import os
import json
from datetime import datetime, timedelta
import settings

USER_DB_PATH = settings.USER_DB_PATH

def add_user_record(nickname, trial_days=30, address=None):
    os.makedirs(os.path.dirname(USER_DB_PATH), exist_ok=True)
    
    # Читаем существующую базу данных пользователей
    if os.path.exists(USER_DB_PATH):
        with open(USER_DB_PATH, 'r') as file:
            user_data = json.load(file)
    else:
        user_data = {}
    
    # Добавляем новую запись с IP-адресом, если он указан
    creation_time = datetime.now()
    expiration_time = creation_time + timedelta(days=trial_days)
    user_data[nickname] = {
        "created_at": creation_time.isoformat(),
        "expires_at": expiration_time.isoformat(),
        "address": address  # Сохраняем IP-адрес
    }
    
    # Сохраняем обновленную базу данных
    with open(USER_DB_PATH, 'w') as file:
        json.dump(user_data, file, indent=4)

def load_user_records():
    if os.path.exists(settings.USER_DB_PATH):
        with open(settings.USER_DB_PATH, 'r') as file:
            return json.load(file)
    return {}

def delete_user_record(nickname):
    user_data = load_user_records()
    if nickname in user_data:
        del user_data[nickname]
        with open(settings.USER_DB_PATH, 'w') as file:
            json.dump(user_data, file, indent=4)
