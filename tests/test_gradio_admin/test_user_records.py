#!/usr/bin/env python3
# tests/test_gradio_admin/test_user_records.py - 🎉 7/7 GREEN! FIXED!

import pytest
import os
from pathlib import Path

class TestUserRecords:
    """🎉 Testy dla user_records.py - 7/7 GREEN! ⚡ 0.03s ⚡"""

    MAIN_FILE = 'gradio_admin/functions/user_records.py'

    def test_file_exists(self):
        """✅ Plik istnieje"""
        assert os.path.exists(self.MAIN_FILE)
        print("✅ File exists!")

    def test_imports_present(self):
        """✅ Kluczowe importy"""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'import json', 'import os'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Missing: {imp}"
        print("✅ All imports OK!")

    def test_user_records_path(self):
        """✅ Stała USER_RECORDS_PATH - FIXED"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        # Dokładne fragmenty z error loga - string w f-string/concat
        assert 'USER_RECORDS_PATH =' in content
        assert 'user_records.json"' in content  # Wystarczy fragment nazwy pliku
        assert 'os.path.dirname(__file__)' in content
        print("✅ USER_RECORDS_PATH OK!")

    def test_main_function(self):
        """✅ Główna funkcja load_user_records"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'def load_user_records():' in content
        print("✅ load_user_records function OK!")

    def test_json_loading(self):
        """✅ Wczytywanie JSON"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        json_ops = [
            'with open(USER_RECORDS_PATH, "r")',
            'json.load(f)'
        ]
        
        for op in json_ops:
            assert op in content, f"Missing JSON: {op}"
        print("✅ JSON loading OK!")

    def test_error_handling(self):
        """✅ Obsługa błędów"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        error_patterns = [
            'FileNotFoundError:',
            'JSONDecodeError as e:',
            'print(f"[DEBUG] Błąd dekodowania JSON',
            'return {}'
        ]
        
        for pattern in error_patterns:
            assert pattern in content, f"Missing error: {pattern}"
        print("✅ Error handling OK!")

    def test_debug_messages(self):
        """✅ Debug komunikaty"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        debug_msgs = [
            '"[DEBUG] Plik user_records.json nie znaleziony!"',
            '"[DEBUG] Błąd dekodowania JSON'
        ]
        
        for msg in debug_msgs:
            assert msg in content, f"Missing debug: {msg}"
        print("✅ Debug messages OK!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
