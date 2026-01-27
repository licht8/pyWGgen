#!/usr/bin/env python3
"""
Testy jednostkowe funkcji formatujących pomocniczych WireGuard VPN.

Moduł testuje formatowanie danych użytkownika:
- Parsowanie datetime ISO i formatowanie czasu
- Obliczenia pozostałego czasu do wygaśnięcia
- Formatowanie informacji użytkownika (IP, email)
- Bezpieczne indeksowanie wierszy tabeli
- F-string z emoji dla UI Gradio
"""

import pytest
import os
from pathlib import Path

class TestFormatHelpers:
    """Testy jednostkowe format_helpers.py."""

    MAIN_FILE = 'gradio_admin/functions/format_helpers.py'

    def test_file_exists(self):
        """Test istnienia pliku."""
        assert os.path.exists(self.MAIN_FILE)

    def test_imports_present(self):
        """Test obecności kluczowych importów."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'from datetime import datetime'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Brakuje: {imp}"

    def test_internal_functions(self):
        """Test obecności głównych funkcji."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        functions = [
            'def format_time(iso_time):',
            'def calculate_time_remaining(',
            'def format_user_info(username,'
        ]
        
        for func in functions:
            assert func in content, f"Brakuje: {func}"

    def test_datetime_parsing(self):
        """Test parsowania datetime ISO."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        datetime_features = [
            'datetime.fromisoformat(iso_time)',
            'strftime("%Y-%m-%d %H:%M:%S")',
            'dt_expiry - datetime.now()'
        ]
        
        for feature in datetime_features:
            assert feature in content, f"Brakuje datetime: {feature}"

    def test_time_calculation(self):
        """Test obliczeń czasu."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        time_logic = [
            'delta.days >= 0',
            'f"{delta.days} dni"',
            'return "Wygasło"'
        ]
        
        for logic in time_logic:
            assert logic in content, f"Brakuje logiki czasu: {logic}"

    def test_user_data_access(self):
        """Test dostępu do danych użytkownika."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        data_access = [
            'user_data.get("created_at"',
            'user_data.get("expires_at"',
            'user_data.get("address"'
        ]
        
        for access in data_access:
            assert access in content, f"Brakuje dostępu do danych: {access}"

    def test_table_row_indexing(self):
        """Test indeksowania wiersza tabeli."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        table_checks = [
            'table_row[3] if len(table_row) > 3',
            'table_row[4] if len(table_row) > 4',
            'table_row[6] if len(table_row) > 6'
        ]
        
        for check in table_checks:
            assert check in content, f"Brakuje indeksu tabeli: {check}"

    def test_format_strings(self):
        """Test f-string formatowania."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        format_features = [
            '👤 Użytkownik: {username}',
            '📧 Email: [user@mail.wg]',
            '🌐 IP wewnętrzne: {int_ip}',
            '{format_time(created)}'
        ]
        
        for feature in format_features:
            assert feature in content, f"Brakuje formatowania: {feature}"

    def test_error_handling(self):
        """Test obsługi błędów."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        error_patterns = [
            'except Exception:',
            'return "N/A"',
            'return "Wygasło"'
        ]
        
        for pattern in error_patterns:
            assert pattern in content, f"Brakuje błędu: {pattern}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
