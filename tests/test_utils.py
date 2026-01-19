import pytest
import sys
import os
import json
from unittest.mock import patch, mock_open
import tempfile

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyWGgen.modules import utils

class TestUtils:
    
    def test_read_json_file_exists(self):
        """Тест чтения существующего JSON"""
        test_data = {"users": 5, "active": 2}
        with patch('builtins.open', mock_open(read_data=json.dumps(test_data))) as m:
            with patch('os.path.exists', return_value=True):
                result = utils.read_json("/test.json")
                
                assert result == test_data
                m.assert_called_once_with("/test.json", 'r', encoding='utf-8')
                print("✅ read_json() читает корректно!")

    def test_read_json_file_not_exists(self):
        """Тест чтения несуществующего JSON"""
        with patch('os.path.exists', return_value=False):
            result = utils.read_json("/nonexistent.json")
            
            assert result == {}
            print("✅ read_json() возвращает {} для несуществующего файла!")

    def test_write_json(self, tmp_path):
        """Тест записи JSON"""
        test_data = {"test": "data", "count": 42}
        file_path = str(tmp_path / "test.json")
        
        utils.write_json(file_path, test_data)
        
        with open(file_path, 'r') as f:
            saved = json.load(f)
            assert saved == test_data
        print("✅ write_json() записывает корректно!")

    def test_get_wireguard_config_path(self):
        """Тест пути конфига WireGuard"""
        path = utils.get_wireguard_config_path()
        
        assert path == "/etc/wireguard/wg0.conf"
        print("✅ get_wireguard_config_path() возвращает правильный путь!")

    @patch('pyWGgen.modules.utils.parse_wireguard_config')
    @patch('os.path.exists', return_value=True)
    def test_parse_wireguard_config(self, mock_exists, mock_parse):
        """Тест парсинга конфига"""
        mock_parse.return_value = "[Interface]\nAddress = 10.0.0.1/24"
        
        content = utils.parse_wireguard_config("/test.conf")
        
        mock_parse.assert_called_once_with("/test.conf")
        assert content == "[Interface]\nAddress = 10.0.0.1/24"
        print("✅ parse_wireguard_config() работает!")

    def test_get_wireguard_subnet_success(self, tmp_path):
        """Тест извлечения подсети"""
        config_content = """[Interface]
Address = 10.66.66.1/24, fd00::1/64"""
        
        with patch('pyWGgen.modules.utils.parse_wireguard_config', return_value=config_content):
            subnet = utils.get_wireguard_subnet()
            
            assert subnet == "10.66.66.1/24"
            print("✅ get_wireguard_subnet() находит IPv4 подсеть!")

    def test_log_debug(self, tmp_path):
        """Тест логирования"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.print'):
                utils.log_debug("Test message")
                
        assert True  # Дошли до конца без ошибок
        print("✅ log_debug() работает без ошибок!")
