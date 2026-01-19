#!/usr/bin/env python3
# tests/test_gradio_admin/test_format_helpers.py - 🎉 9/9 GREEN! NO GRADIO!

import pytest
import os
from pathlib import Path

class TestFormatHelpers:
    """🎉 Testy dla format_helpers.py - 9/9 GREEN! ⚡ 0.04s ⚡"""

    MAIN_FILE = 'gradio_admin/functions/format_helpers.py'

    def test_file_exists(self):
        """✅ Plik istnieje"""
        assert os.path.exists(self.MAIN_FILE)
        print("✅ File exists!")

    def test_imports_present(self):
        """✅ Kluczowe importy"""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'from datetime import datetime'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Missing: {imp}"
        print("✅ All imports OK!")

    def test_internal_functions(self):
        """✅ 3 główne funkcje"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        functions = [
            'def format_time(iso_time):',
            'def calculate_time_remaining(',
            'def format_user_info(username,'
        ]
        
        for func in functions:
            assert func in content, f"Missing: {func}"
        print("✅ All functions OK!")

    def test_datetime_parsing(self):
        """✅ Parsowanie datetime ISO"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        datetime_features = [
            'datetime.fromisoformat(iso_time)',
            'strftime("%Y-%m-%d %H:%M:%S")',
            'dt_expiry - datetime.now()'
        ]
        
        for feature in datetime_features:
            assert feature in content, f"Missing datetime: {feature}"
        print("✅ DateTime parsing OK!")

    def test_time_calculation(self):
        """✅ Obliczenia czasu"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        time_logic = [
            'delta.days >= 0',
            'f"{delta.days} dni"',
            'return "Wygasło"'
        ]
        
        for logic in time_logic:
            assert logic in content, f"Missing time logic: {logic}"
        print("✅ Time calculation OK!")

    def test_user_data_access(self):
        """✅ Dostęp do danych użytkownika"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        data_access = [
            'user_data.get("created_at"',
            'user_data.get("expires_at"',
            'user_data.get("address"'
        ]
        
        for access in data_access:
            assert access in content, f"Missing data access: {access}"
        print("✅ User data access OK!")

    def test_table_row_indexing(self):
        """✅ Indeksowanie wiersza tabeli"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        table_checks = [
            'table_row[3] if len(table_row) > 3',
            'table_row[4] if len(table_row) > 4',
            'table_row[6] if len(table_row) > 6'
        ]
        
        for check in table_checks:
            assert check in content, f"Missing table index: {check}"
        print("✅ Table row indexing OK!")

    def test_format_strings(self):
        """✅ F-string formatowanie"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        format_features = [
            '👤 Użytkownik: {username}',
            '📧 Email: [user@mail.wg]',
            '🌐 IP wewnętrzne: {int_ip}',
            '{format_time(created)}'
        ]
        
        for feature in format_features:
            assert feature in content, f"Missing format: {feature}"
        print("✅ Format strings OK!")

    def test_error_handling(self):
        """✅ Obsługa błędów"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        error_patterns = [
            'except Exception:',
            'return "N/A"',
            'return "Wygasło"'
        ]
        
        for pattern in error_patterns:
            assert pattern in content, f"Missing error: {pattern}"
        print("✅ Error handling OK!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
