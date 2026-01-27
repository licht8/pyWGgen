#!/usr/bin/env python3
"""
Testy jednostkowe funkcji pomocniczych tabel WireGuard VPN.

Moduł testuje funkcje table_helpers:
- Importy (json, pandas, USER_DB_PATH)
- Wczytywanie danych z user_records.json
- Filtrowanie nieaktywnych użytkowników
- Struktura tabeli (7 kolumn z danymi transferu)
- Pandas DataFrame z emoji nagłówkami
- Wartości domyślne (N/A, 0.0 KiB, 100.0 GB)
"""

import pytest
import os
from pathlib import Path

class TestTableHelpers:
    """Testy jednostkowe table_helpers.py."""

    MAIN_FILE = 'gradio_admin/functions/table_helpers.py'

    def test_file_exists(self):
        """Test istnienia pliku."""
        assert os.path.exists(self.MAIN_FILE)

    def test_imports_present(self):
        """Test obecności kluczowych importów."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'import os', 'import json', 'pandas as pd',
            'USER_DB_PATH'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Brakuje: {imp}"

    def test_internal_functions(self):
        """Test obecności głównych funkcji."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        functions = [
            'def load_data(show_inactive=True):',
            'def update_table(show_inactive):'
        ]
        
        for func in functions:
            assert func in content, f"Brakuje: {func}"

    def test_json_loading(self):
        """Test wczytywania JSON."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        json_features = [
            'os.path.exists(USER_DB_PATH)',
            'json.load(f)',
            'for username, user_info in users.items():'
        ]
        
        for feature in json_features:
            assert feature in content, f"Brakuje JSON: {feature}"

    def test_data_filtering(self):
        """Test filtrowania nieaktywnych."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        filter_logic = [
            'if not show_inactive and user_info.get("status"',
            'continue'
        ]
        
        for logic in filter_logic:
            assert logic in content, f"Brakuje filtra: {logic}"

    def test_table_structure(self):
        """Test struktury tabeli."""
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
            assert field in content, f"Brakuje pola: {field}"

    def test_pandas_dataframe(self):
        """Test Pandas DataFrame."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        pandas_features = [
            'pd.DataFrame(',
            'columns=["👤 Użytkownik"',
            '"📊 Zużyto"',
            '"🌐 Adres IP"'
        ]
        
        for feature in pandas_features:
            assert feature in content, f"Brakuje pandas: {feature}"

    def test_column_headers(self):
        """Test nagłówków kolumn."""
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
            assert header in content, f"Brakuje nagłówka: {header}"

    def test_default_values(self):
        """Test wartości domyślnych."""
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
            assert default in content, f"Brakuje domyślnej: {default}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
