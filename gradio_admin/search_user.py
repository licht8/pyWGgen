import os
import json
from datetime import datetime

USER_RECORDS_PATH = os.path.join("user", "data", "user_records.json")

def search_user(search_term):
    """Поиск пользователей по частичному совпадению имени или IP."""
    if not os.path.exists(USER_RECORDS_PATH):
        return "❌ Файл user_records.json не найден."

    try:
        with open(USER_RECORDS_PATH, "r") as f:
            user_data = json.load(f)

        result = []
        for username, details in user_data.items():
            if search_term.lower() in username.lower() or search_term in details.get("address", ""):
                created_at = details.get("created_at", "N/A")
                expires_at = details.get("expires_at", "N/A")
                address = details.get("address", "N/A")

                # Рассчитаем оставшееся время
                try:
                    expires_datetime = datetime.fromisoformat(expires_at)
                    remaining_time = expires_datetime - datetime.now()
                    remaining_days = remaining_time.days
                    remaining_str = f"{remaining_days} дней" if remaining_days > 0 else "Истек"
                except Exception:
                    remaining_str = "Ошибка в данных срока действия"

                user_info = (
                    f"👤 Пользователь: {username}\n"
                    f"   📅 Создан: {created_at}\n"
                    f"   ⏳ Истекает: {expires_at}\n"
                    f"   ⏳ Осталось: {remaining_str}\n"
                    f"   🌐 Адрес: {address}"
                )
                result.append(user_info)

        if not result:
            return "ℹ️ Пользователь не найден."

        return "\n\n".join(result)

    except json.JSONDecodeError:
        return "❌ Ошибка чтения файла user_records.json. Проверьте его формат."
