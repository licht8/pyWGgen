import unittest
import sys
import os
from unittest.mock import mock_open, patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.config_writer import add_user_to_server_config, remove_user_from_server_config


class TestConfigWriter(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open)
    def test_add_user_to_server_config(self, mock_open_func):
        """Тест: добавление пользователя в конфигурационный файл."""
        config_file = "mock_config.conf"
        nickname = "testuser"
        public_key = "mock_public_key"
        preshared_key = "mock_preshared_key"
        allowed_ips = "10.0.0.2/32"

        # Вызов функции
        add_user_to_server_config(config_file, nickname, public_key, preshared_key, allowed_ips)

        # Проверяем, что файл открывался в режиме добавления ('a')
        mock_open_func.assert_called_once_with(config_file, 'a')

        # Проверяем содержимое записи
        mock_open_func().write.assert_any_call(f"\n### Client {nickname}\n")
        mock_open_func().write.assert_any_call(f"[Peer]\n")
        mock_open_func().write.assert_any_call(f"PublicKey = {public_key}\n")
        mock_open_func().write.assert_any_call(f"PresharedKey = {preshared_key}\n")
        mock_open_func().write.assert_any_call(f"AllowedIPs = {allowed_ips}\n")

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_remove_user_from_server_config(self, mock_open_func, mock_exists):
        """Тест: удаление пользователя из конфигурационного файла."""
        config_file = "mock_config.conf"
        nickname = "testuser"

        # Исходное содержимое файла
        mock_open_func().readlines.return_value = [
            "### Client testuser\n",
            "[Peer]\n",
            "PublicKey = mock_public_key\n",
            "PresharedKey = mock_preshared_key\n",
            "AllowedIPs = 10.0.0.2/32\n",
            "\n",
            "### Client otheruser\n",
            "[Peer]\n",
            "PublicKey = other_public_key\n",
            "PresharedKey = other_preshared_key\n",
            "AllowedIPs = 10.0.0.3/32\n",
            "\n",
        ]

        # Вызов функции
        remove_user_from_server_config(config_file, nickname)

        # Проверяем, что файл был открыт для чтения и записи
        mock_open_func.assert_any_call(config_file, 'r')
        mock_open_func.assert_any_call(config_file, 'w')

        # Проверяем, что записи testuser удалены
        written_data = "".join(call[0][0] for call in mock_open_func().write.call_args_list)
        expected_data = (
            "### Client otheruser\n"
            "[Peer]\n"
            "PublicKey = other_public_key\n"
            "PresharedKey = other_preshared_key\n"
            "AllowedIPs = 10.0.0.3/32\n"
            "\n"
        )
        self.assertEqual(written_data, expected_data)

    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_remove_user_from_nonexistent_file(self, mock_open_func, mock_exists):
        """Тест: попытка удаления пользователя из несуществующего файла."""
        config_file = "mock_config.conf"
        nickname = "testuser"

        # Вызов функции
        remove_user_from_server_config(config_file, nickname)

        # Проверяем, что open не вызывался
        mock_open_func.assert_not_called()


if __name__ == "__main__":
    unittest.main()
