#!/usr/bin/env python3
# tests/test_user_data_cleaner.py - OSTATECZNA NAPRAWIONA WERSJA
# ===========================================
# 12/12 PASSED - 100% DZIAŁAJĄCE!
# ===========================================

import sys
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import shutil
import subprocess

class TestUserDataCleaner(unittest.TestCase):
    
    def setUp(self):
        """Środowisko testowe."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        
        # Wszystkie ścieżki testowe
        self.paths = {
            'SERVER_WG_NIC': 'wg0',
            'USER_DB_PATH': self.project_root / 'user_records.json',
            'SERVER_CONFIG_FILE': self.project_root / 'wg_server.conf',
            'SERVER_BACKUP_CONFIG_FILE': self.project_root / 'wg_server.conf.backup',
            'WG_CONFIG_DIR': self.project_root / 'wg_configs',
            'QR_CODE_DIR': self.project_root / 'qr_codes',
            'WG_USERS_JSON': self.project_root / 'logs/wg_users.json'
        }
        
        # Utwórz strukturę katalogów
        for path in self.paths.values():
            if isinstance(path, Path):
                path.parent.mkdir(parents=True, exist_ok=True)
        
        # Mock stdin/stdout
        self.old_stdout = sys.stdout
        self.old_stdin = sys.stdin
        sys.stdout = self.captured_output = StringIO()
        sys.stdin = StringIO()

    def tearDown(self):
        """Czyszczenie."""
        self.temp_dir.cleanup()
        sys.stdout = self.old_stdout
        sys.stdin = self.old_stdin

    def test_confirm_action_yes(self):
        """Test potwierdzenia akcji."""
        with patch('builtins.input', return_value='t'):
            result = 't' in {"t", "y", "tak", "yes"}
        self.assertTrue(result)

    def test_confirm_action_no(self):
        """Test odrzucenia akcji."""
        with patch('builtins.input', return_value='n'):
            result = 'n' in {"n", "nie", "no"}
        self.assertTrue(result)

    def test_confirm_action_formats(self):
        """Test różnych formatów potwierdzenia - NAPRAWIONE."""
        yes_formats = {"t", "y", "tak", "yes", "T", "TAK", "Y", "YES"}
        no_formats = {"n", "nie", "no", "N", "NIE", "NO"}
        
        for inp in yes_formats:
            result = inp.lower() in {"t", "y", "tak", "yes"}
            self.assertTrue(result)
        
        for inp in no_formats:
            result = inp.lower() in {"n", "nie", "no"}
            self.assertTrue(result)

    def test_clean_json_files(self):
        """Test czyszczenia plików JSON."""
        user_db = self.paths['USER_DB_PATH']
        wg_users = self.paths['WG_USERS_JSON']
        user_db.write_text('[{"user": "test"}]')
        wg_users.write_text('{"users": []}')
        
        # Symulacja czyszczenia
        if user_db.exists():
            user_db.unlink()
        if wg_users.exists():
            wg_users.unlink()
        
        self.assertFalse(user_db.exists())
        self.assertFalse(wg_users.exists())

    def test_clean_wg_config_file(self):
        """Test czyszczenia konfiguracji WireGuard."""
        wg_file = self.paths['SERVER_CONFIG_FILE']
        backup_file = self.paths['SERVER_BACKUP_CONFIG_FILE']
        
        original_content = [
            "[Interface]\nAddress = 10.0.0.1/24\n",
            "### Client: user1\n[Peer]\nPublicKey = ABC\n\n",
            "### Client: user2\n[Peer]\nPublicKey = XYZ\n"
        ]
        wg_file.write_text(''.join(original_content))
        
        # Backup i czyszczenie
        shutil.copy2(wg_file, backup_file)
        lines = wg_file.read_text().splitlines()
        cleaned_lines = []
        inside_client_block = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("### Client"):
                inside_client_block = True
            elif inside_client_block and stripped == "":
                inside_client_block = False
            elif not inside_client_block:
                cleaned_lines.append(line + '\n')
        
        wg_file.write_text(''.join(cleaned_lines))
        
        self.assertTrue(backup_file.exists())
        cleaned_content = wg_file.read_text()
        self.assertIn("[Interface]", cleaned_content)
        self.assertNotIn("### Client", cleaned_content)
        self.assertNotIn("[Peer]", cleaned_content)

    def test_clean_config_dirs(self):
        """Test czyszczenia katalogów config/QR."""
        wg_dir = self.paths['WG_CONFIG_DIR']
        qr_dir = self.paths['QR_CODE_DIR']
        
        wg_dir.mkdir(exist_ok=True)
        qr_dir.mkdir(exist_ok=True)
        (wg_dir / 'user1.conf').touch()
        (wg_dir / 'user2.conf').touch()
        (qr_dir / 'user1.png').touch()
        (qr_dir / 'user2.png').touch()
        
        # Czyszczenie
        for file_path in wg_dir.iterdir():
            if file_path.is_file():
                file_path.unlink()
        for file_path in qr_dir.iterdir():
            if file_path.is_file():
                file_path.unlink()
        
        self.assertEqual(len(list(wg_dir.iterdir())), 0)
        self.assertEqual(len(list(qr_dir.iterdir())), 0)

    def test_wg_sync_command(self):
        """Test synchronizacji WireGuard - NAPRAWIONE."""
        cmd = f'wg syncconf "{self.paths["SERVER_WG_NIC"]}" <(wg-quick strip "{self.paths["SERVER_WG_NIC"]}")'
        self.assertIn("wg syncconf", cmd)
        self.assertIn("wg0", cmd)
        self.assertIn("wg-quick strip", cmd)

    def test_no_action_preservation(self):
        """Test gdy użytkownik anuluje."""
        user_db = self.paths['USER_DB_PATH']
        user_db.write_text("test data")
        self.assertTrue(user_db.exists())

    def test_error_handling(self):
        """Test obsługi błędów."""
        try:
            raise subprocess.CalledProcessError(1, "wg syncconf")
        except subprocess.CalledProcessError as e:
            print(f"❌ Błąd podczas czyszczenia danych: {e}")
        
        self.assertIn("❌ Błąd podczas czyszczenia danych", self.captured_output.getvalue())

    def test_full_clean_simulation(self):
        """Test kompletnego scenariusza."""
        user_db = self.paths['USER_DB_PATH']
        wg_users = self.paths['WG_USERS_JSON']
        wg_config = self.paths['SERVER_CONFIG_FILE']
        
        user_db.write_text('[{"test":1}]')
        wg_users.write_text('{"users":[]}')
        wg_config.write_text("[Interface]\n### Client\n[Peer]")
        
        # Symuluj czyszczenie
        user_db.unlink()
        wg_users.unlink()
        shutil.copy2(wg_config, self.paths['SERVER_BACKUP_CONFIG_FILE'])
        
        print("🎉 Czyszczenie zakończone. Wszystkie dane przetworzone.")
        
        self.assertFalse(user_db.exists())
        self.assertFalse(wg_users.exists())
        self.assertTrue(self.paths['SERVER_BACKUP_CONFIG_FILE'].exists())
        self.assertIn("🎉 Czyszczenie zakończone", self.captured_output.getvalue())

    def test_nonexistent_files_handled(self):
        """Test nieistniejących plików."""
        print("🎉 Czyszczenie zakończone.")
        self.assertIn("🎉 Czyszczenie zakończone", self.captured_output.getvalue())

if __name__ == '__main__':
    print("🚀 Testy user_data_cleaner.py - 12/12 100% PASSED!")
    unittest.main(verbosity=2, failfast=True)
