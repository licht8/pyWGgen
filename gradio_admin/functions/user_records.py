import json
import os

USER_RECORDS_PATH = os.path.join(os.path.dirname(__file__), "../../user/data/user_records.json")

def load_user_records():
    """Загружает данные о пользователях из файла user_records.json."""
    try:
        with open(USER_RECORDS_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[DEBUG] user_records.json not found!")
        return {}
    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON decode error in user_records.json: {e}")
        return {}
