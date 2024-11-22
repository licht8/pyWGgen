#!/usr/bin/env python3
"""
gradio_admin/wg_users_stats.py

Функции для получения статистики пользователей WireGuard.
"""

import os
import json

# Путь к файлу JSON
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JSON_LOG_PATH = os.path.join(PROJECT_ROOT, "logs/wg_users.json")


def load_data(show_inactive):
    """
    Загружает данные пользователей WireGuard из JSON-файла и фильтрует их.
    
    :param show_inactive: Флаг, показывать ли неактивных пользователей.
    :return: Таблица для отображения в Gradio.
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

    users = data.get("users", {})
    print(f"Загруженные пользователи: {users}")  # Отладка

    table = []

    for username, user_data in users.items():
        # Если show_inactive == False, пропускаем неактивных пользователей
        if not show_inactive and user_data["status"] == "inactive":
            continue
        table.append([
            username or "Неизвестно",  # Имя пользователя
            ", ".join(user_data.get("endpoints", ["Нет данных"])),  # Список Endpoints
            user_data.get("allowed_ips", "Нет данных"),  # Разрешенные IPs
            user_data["total_transfer"]["received"],  # Принятый трафик
            user_data["total_transfer"]["sent"],  # Отправленный трафик
            user_data["last_handshake"] or "Никогда",  # Последний Handshake
            "Активен" if user_data["status"] == "active" else "Неактивен"  # Статус пользователя
        ])

    print(f"Форматированная таблица перед возвратом: {table}")  # Отладка
    return table


# Gradio-приложение для тестирования
def create_gradio_app():
    """
    Создает Gradio-приложение для отображения статистики пользователей WireGuard.
    """
    import gradio as gr

    with gr.Blocks() as app:
        gr.Markdown("### Статистика пользователей WireGuard")

        show_inactive = gr.Checkbox(label="Показать неактивных пользователей", value=True)
        stats_table = gr.Dataframe(
            headers=["Пользователь", "Endpoints", "Разрешенные IPs", "Принято", "Отправлено", "Handshake", "Статус"],
            interactive=False
        )

        def update_table(show_inactive):
            table = load_data(show_inactive)
            print(f"Обновленная таблица: {table}")
            return table

        show_inactive.change(fn=update_table, inputs=[show_inactive], outputs=[stats_table])

    return app


# Основная точка входа для запуска приложения
if __name__ == "__main__":
    app = create_gradio_app()
    app.launch(server_name="0.0.0.0", server_port=7860, share=True)
