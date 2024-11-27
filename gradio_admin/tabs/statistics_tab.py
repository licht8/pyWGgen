        # Выбор строки и отображение данных пользователя
        def show_user_info(selected_data):
            """Показывает информацию о выбранном пользователе."""
            if selected_data is None or len(selected_data) == 0:
                return "Select a row from the table to view details."

            try:
                # Если данные переданы в виде DataFrame
                if isinstance(selected_data, pd.DataFrame):
                    username = selected_data.iloc[0, 0]  # Первый столбец первой строки
                # Если данные переданы в виде списка
                elif isinstance(selected_data, list):
                    username = selected_data[0]  # Первый элемент
                else:
                    return "Unsupported data format selected."

                # Получение данных пользователя
                user_records = load_user_records()
                user_info = user_records.get(username, {})
                if not user_info:
                    return f"No detailed information found for user: {username}"

                # Форматирование информации с эмодзи
                details = [
                    f"👤 **Username**: {user_info.get('username', 'N/A')}",
                    f"📧 **Email**: {user_info.get('email', 'N/A')}",
                    f"📱 **Telegram**: {user_info.get('telegram_id', 'N/A')}",
                    f"🔗 **Allowed IPs**: {user_info.get('allowed_ips', 'N/A')}",
                    f"📊 **Data Used**: {user_info.get('data_used', '0.0 KiB')}",
                    f"📦 **Data Limit**: {user_info.get('data_limit', '100.0 GB')}",
                    f"⚡ **Status**: {user_info.get('status', 'inactive')}",
                    f"💳 **Subscription Plan**: {user_info.get('subscription_plan', 'free')}",
                    f"🛠️ **Public Key**: {user_info.get('public_key', 'N/A')}",
                    f"🔑 **Preshared Key**: {user_info.get('preshared_key', 'N/A')}",
                ]
                return "\n".join(details)
            except Exception as e:
                return f"Error processing user information: {str(e)}"
