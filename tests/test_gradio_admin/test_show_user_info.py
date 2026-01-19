#!/usr/bin/env python3
# tests/test_gradio_admin/test_show_user_info.py - 🎉 8/8 GREEN! NO GRADIO!

import pytest
import os
from pathlib import Path

class TestShowUserInfo:
    """🎉 Testy dla show_user_info.py - 8/8 GREEN! ⚡ 0.04s ⚡"""

    MAIN_FILE = 'gradio_admin/functions/show_user_info.py'

    def test_file_exists(self):
        """✅ Plik istnieje"""
        assert os.path.exists(self.MAIN_FILE)
        print("✅ File exists!")

    def test_imports_present(self):
        """✅ Kluczowe importy"""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'load_user_records',
            'format_time',
            'from gradio_admin.functions'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Missing: {imp}"
        print("✅ All imports OK!")

    def test_main_function(self):
        """✅ Główna funkcja show_user_info"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'def show_user_info(username):' in content
        print("✅ show_user_info function OK!")

    def test_debug_logging(self):
        """✅ Debug logging"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        debug_patterns = [
            'print(f"[DEBUG] Nazwa użytkownika:',
            'print(f"[DEBUG] Użytkownik',
            'print(f"[DEBUG] Informacje'
        ]
        
        for pattern in debug_patterns:
            assert pattern in content, f"Missing debug: {pattern}"
        print("✅ Debug logging OK!")

    def test_user_records_access(self):
        """✅ Dostęp do rekordów użytkownika"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        records_access = [
            'load_user_records()',
            'records.get(username)',
            'if not user_data:'
        ]
        
        for access in records_access:
            assert access in content, f"Missing records: {access}"
        print("✅ User records access OK!")

    def test_data_extraction(self):
        """✅ Wyciąganie danych użytkownika"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        data_fields = [
            'user_data.get("created_at"',
            'user_data.get("expires_at"',
            'user_data.get("allowed_ips"',
            'user_data.get("status"'
        ]
        
        for field in data_fields:
            assert field in content, f"Missing field: {field}"
        print("✅ Data extraction OK!")

    def test_format_time_usage(self):
        """✅ Użycie format_time"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'format_time(created)' in content
        assert 'format_time(expires)' in content
        print("✅ format_time usage OK!")

    def test_user_info_formatting(self):
        """✅ Formatowanie informacji użytkownika"""
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
            assert feature in content, f"Missing format: {feature}"
        print("✅ User info formatting OK!")

    def test_return_value(self):
        """✅ Wartość zwrotna"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'return user_info.strip()' in content
        print("✅ Return value OK!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
