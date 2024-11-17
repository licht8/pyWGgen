import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from datetime import datetime, timedelta
from modules.user_management import add_user_record, load_user_records, delete_user_record
import settings

class TestUserManagement(unittest.TestCase):

    @patch("modules.user_management.settings.USER_DB_PATH", "user/data/user_records.json")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=False)
    @patch("os.makedirs")
    def test_add_user_record(self, mock_makedirs, mock_exists, mock_open_func):
        """Тест добавления нового пользователя."""
        nickname = "testuser"
        trial_days = 30
        address = "10.0.0.1"

        # Вызов тестируемой функции
        add_user_record(nickname, trial_days, address)

        # Определяем ожидаемый каталог, где должен быть создан файл базы данных
        expected_dir = os.path.dirname("user/data/user_records.json")
        mock_makedirs.assert_called_once_with(expected_dir, exist_ok=True)

        # Проверяем, что файл открывается для записи
        mock_open_func.assert_called_with("user/data/user_records.json", "w")

        # Проверяем записанные данные
        handle = mock_open_func()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        parsed_data = json.loads(written_data)

        # Убеждаемся, что данные корректно записаны
        self.assertIn(nickname, parsed_data)
        self.assertEqual(parsed_data[nickname]["address"], address)
        self.assertIn("created_at", parsed_data[nickname])
        self.assertIn("expires_at", parsed_data[nickname])

    @patch("modules.user_management.settings.USER_DB_PATH", "user/data/user_records.json")
    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
        "existinguser": {
            "created_at": "2023-01-01T00:00:00",
            "expires_at": "2023-02-01T00:00:00",
            "address": "10.0.0.2"
        }
    }))
    @patch("os.path.exists", return_value=True)
    def test_add_user_record_existing_file(self, mock_exists, mock_open_func):
        """Тест добавления нового пользователя в существующий файл."""
        nickname = "newuser"
        trial_days = 30
        address = "10.0.0.3"

        # Вызов тестируемой функции
        add_user_record(nickname, trial_days, address)

        # Проверяем, что файл открывается для записи
        mock_open_func.assert_called_with("user/data/user_records.json", "w")

        # Проверяем записанные данные
        handle = mock_open_func()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        parsed_data = json.loads(written_data)

        # Проверяем, что новый пользователь добавлен, а старый не удален
        self.assertIn(nickname, parsed_data)
        self.assertIn("existinguser", parsed_data)
        self.assertEqual(parsed_data[nickname]["address"], address)
        self.assertEqual(parsed_data["existinguser"]["address"], "10.0.0.2")

    @patch("modules.user_management.settings.USER_DB_PATH", "user/data/user_records.json")
    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
        "existinguser": {
            "created_at": "2023-01-01T00:00:00",
            "expires_at": "2023-02-01T00:00:00",
            "address": "10.0.0.2"
        }
    }))
    @patch("os.path.exists", return_value=True)
    def test_delete_user_record_not_found(self, mock_exists, mock_open_func):
        """Тест удаления несуществующего пользователя."""
        nickname = "nonexistentuser"

        delete_user_record(nickname)

        mock_open_func.assert_called_once_with("user/data/user_records.json", "r")
        handle = mock_open_func()
        handle.write.assert_not_called()

    @patch("modules.user_management.settings.USER_DB_PATH", "user/data/user_records.json")
    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
        "existinguser": {
            "created_at": "2023-01-01T00:00:00",
            "expires_at": "2023-02-01T00:00:00",
            "address": "10.0.0.2"
        }
    }))
    @patch("os.path.exists", return_value=True)
    def test_delete_user_record_existing(self, mock_exists, mock_open_func):
        """Тест успешного удаления существующего пользователя."""
        nickname = "existinguser"

        # Вызов тестируемой функции
        delete_user_record(nickname)

        # Проверяем, что файл открывается для записи
        mock_open_func.assert_called_with("user/data/user_records.json", "w")

        # Проверяем записанные данные
        handle = mock_open_func()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        parsed_data = json.loads(written_data)

        # Убедимся, что пользователь удален
        self.assertNotIn(nickname, parsed_data)

    @patch("modules.user_management.settings.USER_DB_PATH", "user/data/user_records.json")
    @patch("builtins.open", new_callable=mock_open, read_data="{}")
    @patch("os.path.exists", return_value=True)
    def test_add_user_with_empty_db(self, mock_exists, mock_open_func):
        """Тест добавления пользователя в пустую базу данных."""
        nickname = "newuser"
        trial_days = 30
        address = "10.0.0.4"

        # Вызов тестируемой функции
        add_user_record(nickname, trial_days, address)

        # Проверяем, что файл открывается для записи
        mock_open_func.assert_called_with("user/data/user_records.json", "w")

        # Проверяем записанные данные
        handle = mock_open_func()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        parsed_data = json.loads(written_data)

        # Убедимся, что пользователь добавлен
        self.assertIn(nickname, parsed_data)
        self.assertEqual(parsed_data[nickname]["address"], address)


if __name__ == "__main__":
    unittest.main()
