import unittest
import json
import os
import sys
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.account_expiry import (
    load_user_records,
    save_user_records,
    check_expiry,
    extend_expiry,
    reset_expiry
)


class TestAccountExpiry(unittest.TestCase):

    def setUp(self):
        # Пример данных для тестов
        self.mock_user_data = {
            "testuser": {
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
            }
        }
        self.mock_file_path = "mock_user_db.json"

    @patch("modules.account_expiry.settings.USER_DB_PATH", "mock_user_db.json")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"testuser": {"expires_at": "2023-12-01T10:00:00"}}))
    def test_load_user_records(self, mocked_open, mocked_exists):
        """Тест: загрузка данных пользователей."""
        user_data = load_user_records()
        mocked_open.assert_called_once_with("mock_user_db.json", "r")
        self.assertEqual(user_data, {"testuser": {"expires_at": "2023-12-01T10:00:00"}})

    @patch("modules.account_expiry.settings.USER_DB_PATH", "mock_user_db.json")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_user_records(self, mocked_open):
        """Тест: сохранение данных пользователей."""
        save_user_records(self.mock_user_data)
        mocked_open.assert_called_once_with("mock_user_db.json", "w")
        written_data = "".join([call[0][0] for call in mocked_open().write.call_args_list])
        self.assertEqual(json.loads(written_data), self.mock_user_data)

    @patch("modules.account_expiry.load_user_records", return_value={
        "testuser": {"expires_at": (datetime.now() + timedelta(days=1)).isoformat()}
    })
    def test_check_expiry_active(self, mocked_load):
        """Тест: проверка активного аккаунта."""
        result = check_expiry("testuser")
        print(f"Result: {result}")
        self.assertEqual(result["status"], "active")

    @patch("modules.account_expiry.load_user_records", return_value={
        "testuser": {"expires_at": (datetime.now() - timedelta(days=1)).isoformat()}
    })
    def test_check_expiry_expired(self, mocked_load):
        """Тест: проверка истекшего аккаунта."""
        result = check_expiry("testuser")
        self.assertEqual(result["status"], "expired")
        self.assertEqual(result["remaining_time"], "Срок действия истек")

    @patch("modules.account_expiry.load_user_records", return_value={"testuser": {"expires_at": "2023-12-01T10:00:00"}})
    @patch("modules.account_expiry.save_user_records")
    def test_extend_expiry(self, mocked_save, mocked_load):
        """Тест: продление срока действия аккаунта."""
        extend_expiry("testuser", 10)
        updated_data = mocked_save.call_args[0][0]
        new_expiry = datetime.fromisoformat(updated_data["testuser"]["expires_at"])
        expected_expiry = datetime(2023, 12, 1, 10, 0, 0) + timedelta(days=10)
        self.assertEqual(new_expiry, expected_expiry)

    @patch("modules.account_expiry.load_user_records", return_value={"testuser": {"expires_at": "2023-12-01T10:00:00"}})
    @patch("modules.account_expiry.save_user_records")
    def test_reset_expiry(self, mocked_save, mocked_load):
        """Тест: сброс срока действия аккаунта."""
        reset_expiry("testuser", trial_days=15)
        updated_data = mocked_save.call_args[0][0]
        new_expiry = datetime.fromisoformat(updated_data["testuser"]["expires_at"])
        expected_expiry = datetime.now() + timedelta(days=15)
        self.assertAlmostEqual(new_expiry, expected_expiry, delta=timedelta(seconds=5))

    @patch("modules.account_expiry.load_user_records", return_value={})
    def test_check_expiry_user_not_found(self, mocked_load):
        """Тест: пользователь не найден."""
        with self.assertRaises(ValueError) as context:
            check_expiry("unknownuser")
        self.assertEqual(str(context.exception), "Пользователь unknownuser не найден.")


if __name__ == "__main__":
    unittest.main()
