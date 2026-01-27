#!/usr/bin/env python3
"""
Testy jednostkowe funkcji wyświetlania informacji o użytkowniku WireGuard VPN.

Moduł testuje funkcję show_user_info:
- Importy (load_user_records, format_time)
- Debug logging z prefixem [DEBUG]
- Dostęp do rekordów użytkownika z user_records.json
- Wyciąganie pól (created_at, expires_at, allowed_ips, status)
- Użycie format_time dla dat
- F-string formatowanie z emoji
"""

import pytest
import os
from pathlib import Path

class TestShowUserInfo:
    """Testy jednostkowe show_user_info.py."""

    MAIN_FILE = 'gradio_admin/functions/show_user_info.py'

    def test_file_exists(self):
        """Test istnienia pliku."""
        assert os.path.exists(self.MAIN_FILE)

    def test_imports_present(self):
        """Test obecności kluczowych importów."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'load_user_records',
            'format_time',
            'from gradio_admin.functions'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Brakuje: {imp}"

    def test_main_function(self):
        """Test głównej funkcji show_user_info."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'def show_user_info(username):' in content

    def test_debug_logging(self):
        """Test debug logging."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        debug_patterns = [
            'print(f"[DEBUG] Nazwa użytkownika:',
            'print(f"[DEBUG] Użytkownik',
            'print(f"[DEBUG] Informacje'
        ]
        
        for pattern in debug_patterns:
            assert pattern in content, f"Brakuje debug: {pattern}"

    def test_user_records_access(self):
        """Test dostępu do rekordów użytkownika."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        records_access = [
            'load_user_records()',
            'records.get(username)',
            'if not user_data:'
        ]
        
        for access in records_access:
            assert access in content, f"Brakuje rekordów: {access}"

    def test_data_extraction(self):
        """Test wyciągania danych użytkownika."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        data_fields = [
            'user_data.get("created_at"',
            'user_data.get("expires_at"',
            'user_data.get("allowed_ips"',
            'user_data.get("status"'
        ]
        
        for field in data_fields:
            assert field in content, f"Brakuje pola: {field}"

    def test_format_time_usage(self):
        """Test użycia format_time."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'format_time(created)' in content
        assert 'format_time(expires)' in content

    def test_user_info_formatting(self):
        """Test formatowania informacji użytkownika."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        format_features = [
            '👤 Użytkownik: {username}',
            '📧 Email: {email}',
            '🌐 IP wewnętrzne: {int_ip}',
            '⚡ Status: {status}',
            '📝 Notatki: {notes}'
        ]
        
        for feature in format_features:
            assert feature in content, f"Brakuje formatowania: {feature}"

    def test_return_value(self):
        """Test wartości zwrotnej."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'return user_info.strip()' in content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
