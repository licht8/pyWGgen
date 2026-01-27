#!/usr/bin/env python3
"""
Testy jednostkowe funkcji głównych modułu main.

Moduł testuje kluczowe funkcje:
- Obliczanie podsieci z adresu IP
- Generowanie następnego wolnego IP z konfiguracji wg0.conf
- Ładowanie istniejących użytkowników
- Sprawdzanie obecności użytkownika w konfiguracji serwera
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
import tempfile
import ipaddress

# Dodajemy korzeń projektu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestMain:
    
    @patch.dict(sys.modules, {'qrcode': Mock(), 'settings': Mock()})
    def test_calculate_subnet_success(self):
        """Test poprawnego obliczania podsieci."""
        import main
        result = main.calculate_subnet("10.66.66.1")
        assert result == "10.66.66.0/24"

    @patch.dict(sys.modules, {'qrcode': Mock(), 'settings': Mock()})
    def test_calculate_subnet_invalid(self):
        """Test niepoprawnego adresu IP."""
        import main
        result = main.calculate_subnet("999.999.999")
        assert result == "10.66.66.0/24"

    @patch.dict(sys.modules, {'qrcode': Mock(), 'settings': Mock()})
    def test_generate_next_ip_empty(self, tmp_path):
        """Test pierwszego dostępnego IP."""
        import main
        config_path = str(tmp_path / "wg0.conf")
        result = main.generate_next_ip(config_path, "10.66.66.0/24")
        assert result == "10.66.66.2"

    @patch.dict(sys.modules, {'qrcode': Mock(), 'settings': Mock()})
    def test_generate_next_ip_skip_used(self, tmp_path):
        """Test pomijania zajetego IP."""
        import main
        config_path = str(tmp_path / "wg0.conf")
        with open(config_path, "w") as f:
            f.write("[Peer]\nAllowedIPs = 10.66.66.2/32")
        result = main.generate_next_ip(config_path, "10.66.66.0/24")
        assert result == "10.66.66.3"

    @patch.dict(sys.modules, {'qrcode': Mock(), 'settings': Mock()})
    def test_load_existing_users_empty(self):
        """Test pustej bazy użytkowników."""
        import main
        with patch('main.os.path.exists', return_value=False):
            result = main.load_existing_users()
        assert result == {}

    @patch.dict(sys.modules, {'qrcode': Mock(), 'settings': Mock()})
    def test_is_user_in_server_config(self, tmp_path):
        """Test wyszukiwania użytkownika w konfiguracji serwera."""
        import main
        config_path = str(tmp_path / "wg0.conf")
        with open(config_path, "w") as f:
            f.write("testuser\n[Peer]")
        result = main.is_user_in_server_config("testuser", config_path)
        assert result == True
