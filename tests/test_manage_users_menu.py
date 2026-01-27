#!/usr/bin/env python3
"""
Testy jednostkowe modułu zarządzania użytkownikami.

Moduł testuje operacje na użytkownikach WireGuard:
- Tworzenie katalogów dla plików konfiguracyjnych
- Wczytywanie bazy danych użytkowników
- Wyodrębnianie kluczy publicznych z konfiguracji wg0.conf
- Usuwanie sekcji Peer z konfiguracji serwera
- Pełny flow usuwania użytkownika z systemem
"""

import pytest
import os
import json
import sys
from unittest.mock import Mock, patch
from pathlib import Path

# Import testowanego modułu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.manage_users_menu import (
    ensure_directory_exists, load_user_records, extract_public_key, 
    remove_peer_from_config
)


class TestManageUsersMenu:
    """Testy jednostkowe dla modułu zarządzania użytkownikami."""

    @pytest.fixture
    def sample_user_data(self):
        """Przykładowe dane użytkownika."""
        return {
            "testuser": {
                "allowed_ips": "10.66.66.5/32",
                "status": "active"
            }
        }

    def test_ensure_directory_exists(self, tmp_path):
        """Test tworzenia katalogu jeśli nie istnieje."""
        filepath = tmp_path / "test" / "dir" / "file.conf"
        ensure_directory_exists(str(filepath))
        assert filepath.parent.exists()

    @patch('modules.manage_users_menu.read_json')
    def test_load_user_records_empty(self, mock_read_json):
        """Test wczytywania pustej bazy danych."""
        mock_read_json.return_value = {}
        result = load_user_records()
        assert result == {}

    @patch('modules.manage_users_menu.read_json')
    def test_load_user_records_valid(self, mock_read_json, sample_user_data):
        """Test wczytywania poprawnej bazy danych."""
        mock_read_json.return_value = sample_user_data
        result = load_user_records()
        assert "testuser" in result
        assert result["testuser"]["allowed_ips"] == "10.66.66.5/32"

    def test_extract_public_key_found(self, tmp_path):
        """Test wyodrębniania klucza publicznego - znaleziono."""
        config_path = tmp_path / "wg0.conf"
        config_content = """[Interface]
PrivateKey = server_private_key
Address = 10.0.0.1/24
ListenPort = 51820

### Klient testuser
PublicKey = ABC123xyz...=
AllowedIPs = 10.66.66.5/32
PersistentKeepalive = 25

### Inny klient
PublicKey = DEF456uvw...=
AllowedIPs = 10.66.66.6/32"""
        config_path.write_text(config_content)
        
        result = extract_public_key("testuser", str(config_path))
        assert result == "ABC123xyz...="

    def test_extract_public_key_not_found(self, tmp_path):
        """Test wyodrębniania klucza - nie znaleziono."""
        config_path = tmp_path / "wg0.conf"
        config_content = """[Interface]
PrivateKey = server_private_key

### Klient testuser
PublicKey = ABC123xyz...=
AllowedIPs = 10.66.66.5/32"""
        config_path.write_text(config_content)
        
        result = extract_public_key("nonexistent", str(config_path))
        assert result is None

    def test_remove_peer_from_config(self, tmp_path):
        """Test usuwania sekcji Peer z konfiguracji."""
        config_path = tmp_path / "wg0.conf"
        original_content = """[Interface]
PrivateKey = server_private_key
Address = 10.0.0.1/24
ListenPort = 51820

### Klient testuser
PublicKey = ABC123xyz...=
AllowedIPs = 10.66.66.5/32
PersistentKeepalive = 25

### Inny klient
PublicKey = DEF456uvw...=
AllowedIPs = 10.66.66.6/32"""
        
        config_path.write_text(original_content)
        
        # Sprawdź PRZED
        assert "### Klient testuser" in config_path.read_text()
        assert "### Inny klient" in config_path.read_text()
        
        # Usuń testuser
        remove_peer_from_config("ABC123xyz...=", str(config_path), "testuser")
        
        # Sprawdź PO - pozostałe sekcje muszą zostać
        updated_content = config_path.read_text()
        assert "### Klient testuser" not in updated_content
        assert "ABC123xyz...=" not in updated_content
        assert "PersistentKeepalive = 25" not in updated_content
        
        # Te 2 MUSZĄ ZOSTAĆ:
        assert "PublicKey = DEF456uvw...=" in updated_content
        assert "AllowedIPs = 10.66.66.6/32" in updated_content

    @patch('builtins.input', side_effect=["testuser"])
    @patch('modules.manage_users_menu.subprocess.run')
    @patch('modules.manage_users_menu.os.path.exists')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.unlink')
    @patch('modules.manage_users_menu.write_json')
    @patch('modules.manage_users_menu.read_json')
    @patch('modules.manage_users_menu.extract_public_key')
    def test_delete_user_complete_flow(
        self, mock_extract_key, mock_read_json, mock_write_json,
        mock_unlink, mock_path_exists, mock_os_exists, mock_subprocess, mock_input,
        tmp_path, sample_user_data
    ):
        """Test pełnego przepływu usuwania użytkownika."""
        mock_read_json.return_value = sample_user_data
        mock_extract_key.return_value = "ABC123xyz...="
        mock_os_exists.return_value = True
        mock_path_exists.return_value = True
        mock_subprocess.return_value = Mock(returncode=0)
        
        with patch('settings.USER_DB_PATH', '/tmp/test_users.json'), \
             patch('settings.SERVER_CONFIG_FILE', '/tmp/wg0.conf'), \
             patch('settings.WG_CONFIG_DIR', Path('/tmp/wg')), \
             patch('settings.QR_CODE_DIR', Path('/tmp/qr')), \
             patch('settings.SERVER_WG_NIC', 'wg0'):

            from modules.manage_users_menu import delete_user
            delete_user()

        mock_read_json.assert_called_once()
        mock_write_json.assert_called_once()
        mock_extract_key.assert_called_once()
        mock_subprocess.assert_called()
        mock_unlink.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
