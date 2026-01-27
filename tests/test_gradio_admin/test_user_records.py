#!/usr/bin/env python3
"""
Testy jednostkowe funkcji zarządzania rekordami użytkowników WireGuard VPN.

Moduł testuje operacje user_records.json:
- Importy (json, os)
- Stała USER_RECORDS_PATH z dynamiczną ścieżką
- Funkcja load_user_records()
- Wczytywanie JSON z obsługą błędów
- Debug komunikaty z prefixem [DEBUG]
- Graceful fallback na pusty dict {}
"""

import pytest
import os
from pathlib import Path

class TestUserRecords:
    """Testy jednostkowe user_records.py."""

    MAIN_FILE = 'gradio_admin/functions/user_records.py'

    def test_file_exists(self):
        """Test istnienia pliku."""
        assert os.path.exists(self.MAIN_FILE)

    def test_imports_present(self):
        """Test obecności kluczowych importów."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'import json', 'import os'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Brakuje: {imp}"

    def test_user_records_path(self):
        """Test stałej USER_RECORDS_PATH."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'USER_RECORDS_PATH =' in content
        assert 'user_records.json"' in content
        assert 'os.path.dirname(__file__)' in content

    def test_main_function(self):
        """Test głównej funkcji load_user_records."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'def load_user_records():' in content

    def test_json_loading(self):
        """Test wczytywania JSON."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        json_ops = [
            'with open(USER_RECORDS_PATH, "r")',
            'json.load(f)'
        ]
        
        for op in json_ops:
            assert op in content, f"Brakuje JSON: {op}"

    def test_error_handling(self):
        """Test obsługi błędów."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        error_patterns = [
            'FileNotFoundError:',
            'JSONDecodeError as e:',
            'print(f"[DEBUG] Błąd dekodowania JSON',
            'return {}'
        ]
        
        for pattern in error_patterns:
            assert pattern in content, f"Brakuje błędu: {pattern}"

    def test_debug_messages(self):
        """Test komunikatów debug."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        debug_msgs = [
            '"[DEBUG] Plik user_records.json nie znaleziony!"',
            '"[DEBUG] Błąd dekodowania JSON'
        ]
        
        for msg in debug_msgs:
            assert msg in content, f"Brakuje debug: {msg}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
