#!/usr/bin/env python3
# modules/user_data_cleaner.py
# Модуль для очистки данных пользователей

import os
import shutil

USER_DATA_DIR = "user/data"
USER_LOGS_DIR = "logs"
USER_RECORDS_JSON = "user/data/user_records.json"

def clean_user_data():
    """Удаляет устаревшие данные пользователей."""
    try:
        # Удаление папки с данными пользователей
        if os.path.exists(USER_DATA_DIR):
            shutil.rmtree(USER_DATA_DIR)
            print(f"✅ Папка {USER_DATA_DIR} успешно очищена.")

        # Удаление логов
        if os.path.exists(USER_LOGS_DIR):
            shutil.rmtree(USER_LOGS_DIR)
            print(f"✅ Папка {USER_LOGS_DIR} успешно очищена.")

        # Удаление JSON-файла с пользователями
        if os.path.exists(USER_RECORDS_JSON):
            os.remove(USER_RECORDS_JSON)
            print(f"✅ Файл {USER_RECORDS_JSON} успешно удален.")

        print("🧹 База пользователей успешно очищена!")
    except Exception as e:
        print(f"❌ Ошибка при очистке данных: {e}")
