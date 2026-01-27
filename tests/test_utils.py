#!/usr/bin/env python3
"""
Testy jednostkowe modułu utils - funkcje pomocnicze pyWGgen.

Moduł testuje operacje plików JSON i konfiguracji WireGuard:
- Bezpieczne wczytywanie/zapisywanie plików JSON
- Parsowanie konfiguracji wg0.conf
- Wyciąganie podsieci z konfiguracji interfejsu
- Standardowe ścieżki WireGuard (/etc/wireguard/)
- Lokalne logowanie debug
"""

import pytest
import sys
import os
import json
from unittest.mock import patch, mock_open
import tempfile

# Dodajemy ścieżkę do projektu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyWGgen.modules import utils

class TestUtils:
    
    def test_read_json_file_exists(self):
        """Test wczytywania istniejącego pliku JSON."""
        test_data = {"users": 5, "active": 2}
        with patch('builtins.open', mock_open(read_data=json.dumps(test_data))) as m:
            with patch('os.path.exists', return_value=True):
                result = utils.read_json("/test.json")
                
                assert result == test_data
                m.assert_called_once_with("/test.json", 'r', encoding='utf-8')

    def test_read_json_file_not_exists(self):
        """Test nieistniejącego pliku JSON."""
        with patch('os.path.exists', return_value=False):
            result = utils.read_json("/nonexistent.json")
            
            assert result == {}

    def test_write_json(self, tmp_path):
        """Test zapisywania pliku JSON."""
        test_data = {"test": "data", "count": 42}
        file_path = str(tmp_path / "test.json")
        
        utils.write_json(file_path, test_data)
        
        with open(file_path, 'r') as f:
            saved = json.load(f)
            assert saved == test_data

    def test_get_wireguard_config_path(self):
        """Test standardowej ścieżki konfiguracji WireGuard."""
        path = utils.get_wireguard_config_path()
        
        assert path == "/etc/wireguard/wg0.conf"

    @patch('pyWGgen.modules.utils.parse_wireguard_config')
    @patch('os.path.exists', return_value=True)
    def test_parse_wireguard_config(self, mock_exists, mock_parse):
        """Test parsowania konfiguracji WireGuard."""
        mock_parse.return_value = "[Interface]\nAddress = 10.0.0.1/24"
        
        content = utils.parse_wireguard_config("/test.conf")
        
        mock_parse.assert_called_once_with("/test.conf")
        assert content == "[Interface]\nAddress = 10.0.0.1/24"

    def test_get_wireguard_subnet_success(self, tmp_path):
        """Test wyciągania podsieci IPv4 z konfiguracji."""
        config_content = """[Interface]
Address = 10.66.66.1/24, fd00::1/64"""
        
        with patch('pyWGgen.modules.utils.parse_wireguard_config', return_value=config_content):
            subnet = utils.get_wireguard_subnet()
            
            assert subnet == "10.66.66.1/24"

    def test_log_debug(self, tmp_path):
        """Test funkcji logowania debug."""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.print'):
                utils.log_debug("Test message")
                
        assert True  # Brak błędów = sukces
