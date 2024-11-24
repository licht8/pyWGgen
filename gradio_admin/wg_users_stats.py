#!/usr/bin/env python3
# gradio_admin/wg_users_stats.py
# Скрипт для работы со статистикой пользователей WireGuard в проекте wg_qr_generator

import os
import json

# Путь к файлу JSON
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JSON_LOG_PATH = os.path.join(PROJECT_ROOT, "logs/wg_users.json")


def load_data(show_inactive):
    """
    Загружает данные пользователей WireGuard из JSON-файла и фильтрует их.
    """
    try:
        print(f"Путь к JSON: {JSON_LOG_PATH}")  # Отладка
        with open(JSON_LOG_PATH, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("JSON-файл не найден!")
        return [["Нет данных о пользователях"]]
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")
        return [["Ошибка чтения JSON-файла"]]

    # Логика работы с верхним уровнем JSON
    print(f"Загруженные пользователи: {data}")  # Отладка

    table = []

    for username, user_data in data.items():
        # Пропускаем пользователей со статусом "inactive", если show_inactive == False
        if not show_inactive and user_data.get("status") == "inactive":
            continue

        # Форматируем статус
        status_color = "green" if user_data.get("status") == "active" else "red"
        status_html = f"<span style='color: {status_color}'>{user_data.get('status', 'unknown')}</span>"

        # Добавляем строку в таблицу
        table.append([
            username,
            user_data.get("endpoint", "N/A"),
            user_data.get("allowed_ips", "N/A"),
            user_data.get("uploaded", "N/A"),
            user_data.get("downloaded", "N/A"),
            user_data.get("last_handshake", "N/A"),
            status_html
        ])

    print(f"Форматированная таблица перед возвратом: {table}")  # Отладка
    return table


if __name__ == "__main__":
    # Тестовая загрузка данных для отладки
    print("Тестовая загрузка данных...")
    test_data = load_data(show_inactive=True)
    for row in test_data:
        print(row)
