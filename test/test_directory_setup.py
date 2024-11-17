import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, mock_open, call
from modules.directory_setup import setup_directories


class TestDirectorySetup(unittest.TestCase):

    @patch("os.makedirs")
    @patch("os.path.exists", side_effect=lambda path: path != "user/data/user_records.json")
    @patch("builtins.open", new_callable=mock_open)
    @patch("modules.directory_setup.settings", create=True)
    def test_setup_directories(self, mock_settings, mock_open_func, mock_exists, mock_makedirs):
        """Тест: создание директорий и файла базы данных пользователей."""

        # Настраиваем значения для настроек
        mock_settings.WG_CONFIG_DIR = "mock_wg_config"
        mock_settings.QR_CODE_DIR = "mock_qr_code"
        mock_settings.STALE_CONFIG_DIR = "mock_stale_config"
        mock_settings.USER_DB_PATH = "user/data/user_records.json"

        # Вызов функции
        setup_directories()

        # Проверяем, что os.makedirs был вызван для каждой директории
        expected_directories = [
            "mock_wg_config",
            "mock_qr_code",
            "mock_stale_config",
            "user/data"
        ]
        for directory in expected_directories:
            mock_makedirs.assert_any_call(directory, exist_ok=True)

        # Проверяем, что open был вызван для создания USER_DB_PATH
        mock_open_func.assert_called_once_with("user/data/user_records.json", "w")
        mock_open_func().write.assert_called_once_with("{}")  # Проверяем только '{}'

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    @patch("modules.directory_setup.settings", create=True)
    def test_user_db_path_already_exists(self, mock_settings, mock_open_func, mock_exists):
        """Тест: файл USER_DB_PATH уже существует, open не вызывается."""

        # Настраиваем значения для настроек
        mock_settings.WG_CONFIG_DIR = "mock_wg_config"
        mock_settings.QR_CODE_DIR = "mock_qr_code"
        mock_settings.STALE_CONFIG_DIR = "mock_stale_config"
        mock_settings.USER_DB_PATH = "user/data/user_records.json"

        # Вызов функции
        setup_directories()

        # Проверяем, что open не вызывается, так как файл существует
        mock_open_func.assert_not_called()


if __name__ == "__main__":
    unittest.main()
