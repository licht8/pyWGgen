#!/usr/bin/env python3
# ai_diagnostics/ai_diagnostics_summary.py
# Скрипт для создания обобщенного отчета о состоянии проекта wg_qr_generator.
# Версия: 1.0
# Обновлено: 2024-12-02

import json
import os
import subprocess
import matplotlib.pyplot as plt
from pathlib import Path

# Путь к корневой директории проекта
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = PROJECT_ROOT / "user" / "data" / "logs"
USER_DB_PATH = PROJECT_ROOT / "user" / "data" / "user_records.json"
WG_CONFIG_DIR = PROJECT_ROOT / "user" / "data" / "wg_configs"

def load_user_data(user_db_path):
    """Загружает данные пользователей из user_records.json."""
    if user_db_path.exists():
        with open(user_db_path, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print(" ❌ Ошибка: Невозможно прочитать user_records.json.")
                return []
    else:
        print(" ❌ Файл user_records.json отсутствует.")
        return []

def count_wg_peers(wg_config_dir):
    """Считает количество peer в конфигурациях WireGuard."""
    if not wg_config_dir.exists():
        print(" ❌ Директория с конфигурациями WireGuard отсутствует.")
        return 0
    return sum(1 for file in wg_config_dir.glob("*.conf"))

def check_gradio_port(port=7860):
    """Проверяет доступность порта Gradio."""
    command = f"lsof -i:{port}"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode == 0

def generate_graph(user_count, peer_count):
    """Создает график для визуализации количества пользователей и peer."""
    labels = ["Users", "Peers"]
    values = [user_count, peer_count]
    plt.bar(labels, values)
    plt.title("Users vs. Peers")
    plt.ylabel("Count")
    plt.savefig(LOGS_DIR / "users_vs_peers.png")
    print(f" 📊 График сохранен: {LOGS_DIR / 'users_vs_peers.png'}")

def generate_summary_report(user_count, peer_count, is_gradio_running):
    """Создает текстовый обобщенный отчет."""
    report = f"""
=== 📋 Обобщенный отчет о состоянии проекта ===

📂 Пользователи:
- Общее количество пользователей: {user_count}

🔒 WireGuard:
- Общее количество peer: {peer_count}

🌐 Gradio:
- Статус: {"Запущен" if is_gradio_running else "Не запущен"}
- Для запуска: 
  1️⃣ Перейдите в директорию проекта: cd {PROJECT_ROOT}
  2️⃣ Выполните команду: python3 main.py

🎯 Рекомендации:
- Убедитесь, что количество peer совпадает с количеством пользователей.
- Если Gradio не запущен, выполните предложенные действия.

"""
    summary_path = LOGS_DIR / "summary_report.txt"
    with open(summary_path, "w", encoding="utf-8") as file:
        file.write(report)
    print(f"📄 Обобщенный отчет сохранен: {summary_path}")

def main():
    """Основной запуск программы."""
    print("🤖 Создание обобщенного отчета...")

    # Загружаем данные пользователей
    user_data = load_user_data(USER_DB_PATH)
    user_count = len(user_data)

    # Считаем количество peer
    peer_count = count_wg_peers(WG_CONFIG_DIR)

    # Проверяем доступность Gradio
    is_gradio_running = check_gradio_port()

    # Генерируем график
    generate_graph(user_count, peer_count)

    # Создаем текстовый отчет
    generate_summary_report(user_count, peer_count, is_gradio_running)

if __name__ == "__main__":
    main()
