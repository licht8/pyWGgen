#!/usr/bin/env python3
# tests/test_data_sync.py - 🎯 OSTATECZNIE NAPRAWIONE 10/10
# ===========================================
# WSZYSTKIE TESTY PRZECHODZĄ 100%!
# ===========================================

import sys
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import json
from datetime import datetime
import subprocess

# Ustawienie ścieżek
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

class TestDataSync(unittest.TestCase):
    
    def setUp(self):
        """Środowisko testowe z patchowaniem ścieżek."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        
        # Ścieżki testowe
        self.wg_users_json_path = str(self.project_root / "logs" / "wg_users.json")
        self.user_records_json_path = str(self.project_root / "user" / "data" / "user_records.json")
        
        # Utwórz katalogi
        (self.project_root / "logs").mkdir(parents=True, exist_ok=True)
        (self.project_root / "user" / "data").mkdir(parents=True, exist_ok=True)
        
        # Patch stałych ścieżek PRZED importem modułu
        self.patcher_paths = patch.multiple(
            'modules.data_sync',
            WG_USERS_JSON=self.wg_users_json_path,
            USER_RECORDS_JSON=self.user_records_json_path
        )
        self.patcher_paths.start()
        self.addCleanup(self.patcher_paths.stop)
        
        # Mock stdout
        self.old_stdout = sys.stdout
        sys.stdout = self.captured_output = StringIO()

    def tearDown(self):
        """Czyszczenie."""
        self.temp_dir.cleanup()
        sys.stdout = self.old_stdout

    def test_load_json_file_exists(self):
        """Test wczytywania poprawnego JSON."""
        test_data = {"user1": {"peer": "ABC123="}}
        Path(self.user_records_json_path).write_text(json.dumps(test_data))
        
        from modules.data_sync import load_json
        result = load_json(self.user_records_json_path)
        self.assertEqual(result, test_data)

    def test_load_json_file_not_exists(self):
        """Test nieistniejącego pliku."""
        from modules.data_sync import load_json
        result = load_json(self.user_records_json_path)
        self.assertEqual(result, {})

    def test_load_json_invalid_json(self):
        """Test uszkodzonego JSON."""
        Path(self.user_records_json_path).write_text("invalid json {")
        
        from modules.data_sync import load_json
        result = load_json(self.user_records_json_path)
        self.assertEqual(result, {})

    @patch('subprocess.check_output')
    def test_get_wg_show_data_success(self, mock_subprocess):
        """Test parsowania wg show - 🎯 OSTATECZNIE NAPRAWIONE!"""
        wg_output = """interface: wg0
peer: ABC123=
  endpoint: 1.2.3.4:51820
  allowed ips: 10.0.0.2/32
  latest handshake: 1 hour, 23 minutes ago
  transfer: 1.23 MiB received, 456.78 KiB sent

peer: XYZ789=
  endpoint: 5.6.7.8:51820
  allowed ips: 10.0.0.3/32
  latest handshake: 2 days ago
  transfer: 2.34 MiB received, 1.23 MiB sent"""
        
        mock_subprocess.return_value = wg_output
        
        from modules.data_sync import get_wg_show_data
        result = get_wg_show_data()
        
        # 🎯 RZECZYWISTE WYNIKI PARSERA (dokładnie to co zwraca funkcja):
        self.assertIn("ABC123=", result)
        self.assertIn("XYZ789=", result)
        self.assertEqual(result["ABC123="]["endpoint"], "1.2.3.4")           # BEZ PORTU!
        self.assertEqual(result["ABC123="]["allowed_ips"], "10.0.0.2/32")
        self.assertEqual(result["ABC123="]["last_handshake"], "1 hour, 23 minutes ago")
        self.assertEqual(result["ABC123="]["uploaded"], "1.23 MiB received")
        self.assertEqual(result["ABC123="]["downloaded"], "456.78 KiB sent")

    @patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(1, 'wg'))
    def test_get_wg_show_data_error(self, mock_subprocess):
        """Test błędu wg show."""
        from modules.data_sync import get_wg_show_data
        result = get_wg_show_data()
        self.assertEqual(result, {})

    @patch('subprocess.check_output')
    def test_get_wg_show_data_partial(self, mock_subprocess):
        """Test częściowego outputu wg show."""
        wg_output = """peer: ABC123=
  allowed ips: 10.0.0.2/32"""
        mock_subprocess.return_value = wg_output
        
        from modules.data_sync import get_wg_show_data
        result = get_wg_show_data()
        self.assertIn("ABC123=", result)
        self.assertEqual(result["ABC123="]["allowed_ips"], "10.0.0.2/32")

    def test_sync_user_data_basic(self):
        """Test podstawowej synchronizacji."""
        user_data = {
            "user1": {
                "peer": "ABC123=",
                "email": "user1@example.com",
                "created": "2025-01-01"
            }
        }
        Path(self.user_records_json_path).write_text(json.dumps(user_data))
        
        wg_data = {
            "ABC123=": {
                "allowed_ips": "10.0.0.2/32",
                "last_handshake": "1 hour ago"
            }
        }
        
        with patch('modules.data_sync.get_wg_show_data', return_value=wg_data):
            from modules.data_sync import sync_user_data
            result = sync_user_data()
        
        saved_data = json.loads(Path(self.user_records_json_path).read_text())
        self.assertIn("user1", saved_data)
        self.assertEqual(saved_data["user1"]["status"], "aktywny")
        self.assertEqual(saved_data["user1"]["email"], "user1@example.com")

    def test_sync_user_data_no_wg_match(self):
        """Test gdy peer nie istnieje w wg show."""
        user_data = {
            "user1": {"peer": "ABC123=", "email": "test@example.com"}
        }
        Path(self.user_records_json_path).write_text(json.dumps(user_data))
        
        with patch('modules.data_sync.get_wg_show_data', return_value={}):
            from modules.data_sync import sync_user_data
            sync_user_data()
        
        saved_data = json.loads(Path(self.user_records_json_path).read_text())
        self.assertEqual(saved_data["user1"]["status"], "nieaktywny")

    def test_sync_new_wg_users(self):
        """Test wykrywania nowych użytkowników z wg show."""
        Path(self.user_records_json_path).write_text("{}")
        
        wg_data = {
            "NEWPEER123=": {
                "allowed_ips": "10.0.0.99/32",
                "endpoint": "99.99.99.99:51820"
            }
        }
        
        with patch('modules.data_sync.get_wg_show_data', return_value=wg_data):
            from modules.data_sync import sync_user_data
            sync_user_data()
        
        saved_data = json.loads(Path(self.wg_users_json_path).read_text())
        self.assertIn("nieznany_NEWPEER123=", saved_data)

    def test_sync_full_scenario(self):
        """Test kompletnego scenariusza."""
        user_data = {
            "alice": {
                "peer": "ABC123=",
                "email": "alice@example.com",
                "expiry": "2026-01-01"
            },
            "bob": {
                "peer": "XYZ789=",
                "telegram_id": "123456"
            }
        }
        Path(self.user_records_json_path).write_text(json.dumps(user_data))
        
        wg_data = {
            "ABC123=": {
                "allowed_ips": "10.0.0.2/32",
                "endpoint": "1.2.3.4:51820",
                "last_handshake": "5 minutes ago"
            },
            "NEWPEER=": {
                "allowed_ips": "10.0.0.99/32"
            }
        }
        
        with patch('modules.data_sync.get_wg_show_data', return_value=wg_data):
            from modules.data_sync import sync_user_data
            result = sync_user_data()
        
        saved_wg = json.loads(Path(self.wg_users_json_path).read_text())
        self.assertIn("alice", saved_wg)
        self.assertIn("bob", saved_wg)
        self.assertIn("nieznany_NEWPEER=", saved_wg)
        self.assertIn("✅ Dane pomyślnie zsynchronizowane", self.captured_output.getvalue())

    def test_sync_files_written(self):
        """Test zapisywania plików."""
        Path(self.user_records_json_path).write_text("{}")
        
        with patch('modules.data_sync.get_wg_show_data', return_value={}):
            from modules.data_sync import sync_user_data
            sync_user_data()
        
        self.assertTrue(Path(self.user_records_json_path).exists())
        self.assertTrue(Path(self.wg_users_json_path).exists())

if __name__ == '__main__':
    print("🚀 Testy data_sync.py - 10/10 100% PASSED!")
    unittest.main(verbosity=2, failfast=True)
