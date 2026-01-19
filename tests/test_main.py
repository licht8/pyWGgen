import pytest
import sys
import os
from unittest.mock import Mock, patch
import tempfile
import ipaddress

# Добавляем корень проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestMain:
    
    @patch.dict(sys.modules, {'qrcode': Mock(), 'settings': Mock()})
    def test_calculate_subnet_success(self):
        """✅ Тест вычисления подсети"""
        import main
        result = main.calculate_subnet("10.66.66.1")
        assert result == "10.66.66.0/24"
        print("✅ calculate_subnet() работает!")

    @patch.dict(sys.modules, {'qrcode': Mock(), 'settings': Mock()})
    def test_calculate_subnet_invalid(self):
        """✅ Тест invalid IP"""
        import main
        result = main.calculate_subnet("999.999.999")
        assert result == "10.66.66.0/24"
        print("✅ calculate_subnet() default!")

    @patch.dict(sys.modules, {'qrcode': Mock(), 'settings': Mock()})
    def test_generate_next_ip_empty(self, tmp_path):
        """✅ Тест первого IP"""
        import main
        config_path = str(tmp_path / "wg0.conf")
        result = main.generate_next_ip(config_path, "10.66.66.0/24")
        assert result == "10.66.66.2"
        print("✅ generate_next_ip() первый IP!")

    @patch.dict(sys.modules, {'qrcode': Mock(), 'settings': Mock()})
    def test_generate_next_ip_skip_used(self, tmp_path):
        """✅ Тест занятого IP"""
        import main
        config_path = str(tmp_path / "wg0.conf")
        with open(config_path, "w") as f:
            f.write("[Peer]\nAllowedIPs = 10.66.66.2/32")
        result = main.generate_next_ip(config_path, "10.66.66.0/24")
        assert result == "10.66.66.3"
        print("✅ generate_next_ip() пропуск!")

    @patch.dict(sys.modules, {'qrcode': Mock(), 'settings': Mock()})
    def test_load_existing_users_empty(self):
        """✅ Тест пустой базы"""
        import main
        with patch('main.os.path.exists', return_value=False):
            result = main.load_existing_users()
        assert result == {}
        print("✅ load_existing_users() OK!")

    @patch.dict(sys.modules, {'qrcode': Mock(), 'settings': Mock()})
    def test_is_user_in_server_config(self, tmp_path):
        """✅ Тест поиска пользователя"""
        import main
        config_path = str(tmp_path / "wg0.conf")
        with open(config_path, "w") as f:
            f.write("testuser\n[Peer]")
        result = main.is_user_in_server_config("testuser", config_path)
        assert result == True
        print("✅ is_user_in_server_config() OK!")
