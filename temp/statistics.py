# statistics.py
import json
import os

def get_user_statistics():
    """
    Получение статистики пользователей.
    Возвращает количество пользователей, их список и другие метрики.
    """
    base_dir = os.getcwd()
    user_records_path = os.path.join(base_dir, "user", "data", "user_records.json")

    if not os.path.exists(user_records_path):
        return {
            "status": "error",
            "message": "Файл user_records.json не найден."
        }

    with open(user_records_path, "r") as f:
        users_data = json.load(f)

    total_users = len(users_data)
    user_names = list(users_data.keys())
    return {
        "status": "success",
        "total_users": total_users,
        "user_names": user_names,
    }
