#!/usr/bin/env python3
# test_ip_management.py
## Тесты для модуля ip_management.py

import unittest
import os
import sys
from unittest.mock import patch, mock_open

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем тестируемый модуль
from modules.ip_management import (
    generate_ip,
    get_existing_ips,
)

class TestIPManagement(unittest.TestCase):
    def setUp(self):
        self.mock_config_file = "mock_config_file.conf"
        self.sample_config_content = "AllowedIPs = 10.96.96.2/32\nAllowedIPs = 10.96.96.3/32\n"

    @patch("builtins.open", new_callable=mock_open, read_data="AllowedIPs = 10.96.96.2/32\nAllowedIPs = 10.96.96.3/32\n")
    @patch("os.path.exists", return_value=True)
    def test_get_existing_ips(self, mocked_exists, mocked_open):
        """Тест: извлечение существующих IP из конфигурационного файла."""
        existing_ips = get_existing_ips(self.mock_config_file)
        mocked_open.assert_called_once_with(self.mock_config_file, "r")
        self.assertEqual(
            sorted(existing_ips),
            sorted(["10.96.96.2/32", "10.96.96.3/32"]),
            "Extracted IPs do not match expected data."
        )

    @patch("modules.ip_management.get_existing_ips", return_value={"10.96.96.2/32", "10.96.96.3/32"})
    @patch("modules.utils.get_wireguard_subnet", return_value="10.96.96.1/24")
    def test_generate_ip(self, mocked_get_subnet, mocked_get_existing_ips):
        """Тест: генерация нового IP."""
        new_ip, _ = generate_ip(self.mock_config_file)
        expected_prefix = "10.96.96."
        self.assertTrue(
            new_ip.startswith(expected_prefix),
            f"Generated IP must be in the correct subnet ({expected_prefix})."
        )
        self.assertNotIn(
            new_ip + "/32", mocked_get_existing_ips.return_value,
            "Generated IP must not be in existing IPs."
        )


if __name__ == "__main__":
    unittest.main()
