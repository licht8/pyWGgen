import os
import json

USER_DB_PATH = "user/data/user_records.json"  # Путь к файлу с записями пользователей

def user_exists(nickname):
    """Проверяет, существует ли пользователь с указанным именем."""
    if os.path.exists(USER_DB_PATH):
        with open(USER_DB_PATH, 'r') as file:
            user_data = json.load(file)
            return nickname in user_data
    return False
