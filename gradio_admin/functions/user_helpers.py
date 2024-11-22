"""
user_helpers.py

Функции для работы с пользователями.
"""

import pandas as pd
from .stats_helpers import get_user_info, format_user_data


def show_user_info(selected_data, query):
    """
    Показывает подробную информацию о выбранном пользователе.
    """
    if not query.strip():
        return "Please enter a query to filter user data and then click a cell to view user details."

    if selected_data is None or (isinstance(selected_data, pd.DataFrame) and selected_data.empty):
        return "Select a row from the table!"

    try:
        if isinstance(selected_data, list):
            row = selected_data
        elif isinstance(selected_data, pd.DataFrame):
            row = selected_data.iloc[0].values
        else:
            return "Unsupported data format!"

        username = row[0].replace("👤 User account : ", "") if len(row) > 0 else "N/A"
        user_data = get_user_info(username)
        return format_user_data(user_data, row).strip()
    except Exception as e:
        print(f"[DEBUG] Error in show_user_info: {e}")
        return f"Error processing data: {str(e)}"
