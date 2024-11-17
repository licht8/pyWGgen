import unittest
import os
import json
import sys
from unittest.mock import patch, mock_open

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем тестируемый модуль
from modules.ip_management import (
    generate_ip,
    get_existing_ips,
    load_ip_records,
    save_ip_records,
    release_ip
)

class TestIPManagement(unittest.TestCase):

    def setUp(self):
        self.mock_config_file = "mock_config_file.conf"
        self.mock_ip_db_path = os.path.join(os.path.dirname(__file__), "../user/data/ip_records.json")
        self.sample_ip_records = {"10.66.66.1": True, "10.66.66.2": False}
        self.sample_config_content = "AllowedIPs = 10.66.66.1/32, 10.66.66.2/32\n"

    @patch("modules.ip_management.settings.IP_DB_PATH", os.path.join(os.path.dirname(__file__), "../user/data/ip_records.json"))
    @patch("builtins.open", new_callable=mock_open, read_data='{"10.66.66.1": true, "10.66.66.2": false}')
    def test_load_ip_records(self, mocked_open):
        """Тест: загрузка IP-адресов из JSON файла."""
        ip_records = load_ip_records()
        mocked_open.assert_called_once_with(self.mock_ip_db_path, "r")
        self.assertEqual(ip_records, self.sample_ip_records, "Loaded IP records do not match expected data.")

    @patch("modules.ip_management.settings.IP_DB_PATH", os.path.join(os.path.dirname(__file__), "../user/data/ip_records.json"))
    def test_save_ip_records(self):
        """Тест: сохранение IP-адресов в JSON файл."""
        with patch("builtins.open", mock_open()) as mocked_file:
            save_ip_records(self.sample_ip_records)
            written_data = "".join([call[0][0] for call in mocked_file().write.call_args_list])
            self.assertEqual(
                json.loads(written_data), self.sample_ip_records, "Saved IP records do not match expected data."
            )

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="AllowedIPs = 10.66.66.1/32, 10.66.66.2/32\n")
    def test_get_existing_ips(self, mocked_open, mocked_exists):
        """Тест: извлечение существующих IP из конфигурационного файла."""
        existing_ips = get_existing_ips(self.mock_config_file)
        self.assertEqual(existing_ips, {"10.66.66.1", "10.66.66.2"}, "Extracted IPs do not match expected data.")

    def test_generate_ip(self):
        """Тест: генерация нового IP."""
        existing_ips = {"10.66.66.1", "10.66.66.2"}
        with patch("modules.ip_management.get_existing_ips", return_value=existing_ips):
            result = generate_ip(self.mock_config_file)
            new_ip = result[0] if isinstance(result, tuple) else result
            self.assertTrue(new_ip.startswith("10.66.66."), "Generated IP must start with '10.66.66.'")
            self.assertNotIn(new_ip, existing_ips, "Generated IP must not be in existing IPs")

    @patch("modules.ip_management.load_ip_records", return_value={"10.66.66.1": True, "10.66.66.2": False})
    @patch("modules.ip_management.save_ip_records")
    def test_release_ip(self, mocked_save, mocked_load):
        """Тест: освобождение IP-адреса."""
        ip_to_release = "10.66.66.1"
        release_ip(ip_to_release)
        mocked_save.assert_called_once()
        updated_records = mocked_save.call_args[0][0]
        self.assertFalse(updated_records[ip_to_release], "IP must be marked as available after release")


if __name__ == "__main__":
    unittest.main()
