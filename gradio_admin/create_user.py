import subprocess

def create_user(username):
    """Создание нового пользователя."""
    if not username:
        return "Ошибка: имя пользователя не может быть пустым."
    try:
        subprocess.run(["python3", "main.py", username], check=True)
        return f"✅ Пользователь {username} успешно создан."
    except Exception as e:
        return f"❌ Ошибка при создании пользователя: {str(e)}"
