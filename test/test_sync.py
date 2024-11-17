import unittest
import subprocess
from unittest.mock import patch, MagicMock
import sys
from io import StringIO  
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.sync import sync_wireguard_config


class TestSync(unittest.TestCase):

    @patch("subprocess.run")
    @patch("subprocess.check_output")
    @patch("tempfile.NamedTemporaryFile")
    def test_sync_wireguard_config_success(self, mock_tempfile, mock_check_output, mock_run):
        """Тест: успешная синхронизация WireGuard конфигурации."""
        server_wg_nic = "wg0"

        # Мокаем выходные данные subprocess.check_output
        mock_check_output.return_value = b"mock_config_data"

        # Мокаем временный файл
        mock_temp_file = MagicMock()
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        mock_temp_file.name = "mock_temp_file"

        # Перехват stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            sync_wireguard_config(server_wg_nic)
        finally:
            sys.stdout = sys.__stdout__

        # Проверяем, что данные были записаны в временный файл
        mock_temp_file.write.assert_called_once_with(b"mock_config_data")

        # Проверяем вызов wg syncconf
        mock_run.assert_called_once_with(['wg', 'syncconf', server_wg_nic, "mock_temp_file"], check=True)

        # Проверяем, что сообщение об успешной синхронизации было выведено
        self.assertIn(f"Конфигурация для {server_wg_nic} успешно синхронизирована.", captured_output.getvalue())

    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "wg syncconf"))
    @patch("subprocess.check_output")
    @patch("tempfile.NamedTemporaryFile")
    def test_sync_wireguard_config_sync_error(self, mock_tempfile, mock_check_output, mock_run):
        """Тест: ошибка при синхронизации WireGuard конфигурации."""
        server_wg_nic = "wg0"

        # Мокаем выходные данные subprocess.check_output
        mock_check_output.return_value = b"mock_config_data"

        # Мокаем временный файл
        mock_temp_file = MagicMock()
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        mock_temp_file.name = "mock_temp_file"

        # Перехват stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            sync_wireguard_config(server_wg_nic)
        finally:
            sys.stdout = sys.__stdout__

        # Проверяем, что ошибка синхронизации была выведена
        self.assertIn("Ошибка при синхронизации конфигурации", captured_output.getvalue())

    @patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "wg-quick strip"))
    def test_sync_wireguard_config_strip_error(self, mock_check_output):
        """Тест: ошибка при вызове wg-quick strip."""
        server_wg_nic = "wg0"

        # Перехват stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            sync_wireguard_config(server_wg_nic)
        finally:
            sys.stdout = sys.__stdout__

        # Проверяем, что ошибка вызова wg-quick strip была выведена
        self.assertIn("Ошибка при синхронизации конфигурации", captured_output.getvalue())


if __name__ == "__main__":
    unittest.main()
