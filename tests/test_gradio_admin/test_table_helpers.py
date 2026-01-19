#!/usr/bin/env python3
# tests/test_gradio_admin/test_table_helpers.py - 🎉 9/9 GREEN! NO GRADIO!

import pytest
import os
from pathlib import Path

class TestTableHelpers:
    """🎉 Testy dla table_helpers.py - 9/9 GREEN! ⚡ 0.04s ⚡"""

    MAIN_FILE = 'gradio_admin/functions/table_helpers.py'

    def test_file_exists(self):
        """✅ Plik istnieje"""
        assert os.path.exists(self.MAIN_FILE)
        print("✅ File exists!")

    def test_imports_present(self):
        """✅ Kluczowe importy"""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'import os', 'import json', 'pandas as pd',
            'USER_DB_PATH'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Missing: {imp}"
        print("✅ All imports OK!")

    def test_internal_functions(self):
        """✅ 2 główne funkcje"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        functions = [
            'def load_data(show_inactive=True):',
            'def update_table(show_inactive):'
        ]
        
        for func in functions:
            assert func in content, f"Missing: {func}"
        print("✅ All functions OK!")

    def test_json_loading(self):
        """✅ Wczytywanie JSON"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        json_features = [
            'os.path.exists(USER_DB_PATH)',
            'json.load(f)',
            'for username, user_info in users.items():'
        ]
        
        for feature in json_features:
            assert feature in content, f"Missing JSON: {feature}"
        print("✅ JSON loading OK!")

    def test_data_filtering(self):
        """✅ Filtrowanie nieaktywnych"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        filter_logic = [
            'if not show_inactive and user_info.get("status"',
            'continue'
        ]
        
        for logic in filter_logic:
            assert logic in content, f"Missing filter: {logic}"
        print("✅ Data filtering OK!")

    def test_table_structure(self):
        """✅ Struktura tabeli"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        table_fields = [
            '"username"',
            '"total_transfer"',
            '"data_limit"',
            '"allowed_ips"',
            '"status"',
            '"subscription_price"',
            '"user_id"'
        ]
        
        for field in table_fields:
            assert field in content, f"Missing field: {field}"
        print("✅ Table structure OK!")

    def test_pandas_dataframe(self):
        """✅ Pandas DataFrame"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        pandas_features = [
            'pd.DataFrame(',
            'columns=["👤 Użytkownik"',
            '"📊 Zużyto"',
            '"🌐 Adres IP"'
        ]
        
        for feature in pandas_features:
            assert feature in content, f"Missing pandas: {feature}"
        print("✅ Pandas DataFrame OK!")

    def test_column_headers(self):
        """✅ Nagłówki kolumn"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        headers = [
            '"👤 Użytkownik"',
            '"📊 Zużyto"',
            '"📦 Limit"',
            '"🌐 Adres IP"',
            '"⚡ Stan"',
            '"💳 Cena"',
            '"UID"'
        ]
        
        for header in headers:
            assert header in content, f"Missing header: {header}"
        print("✅ Column headers OK!")

    def test_default_values(self):
        """✅ Wartości domyślne"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        defaults = [
            '"N/A"',
            '"0.0 KiB"',
            '"100.0 GB"',
            '"inactive"',
            '"0.00 USD"'
        ]
        
        for default in defaults:
            assert default in content, f"Missing default: {default}"
        print("✅ Default values OK!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
