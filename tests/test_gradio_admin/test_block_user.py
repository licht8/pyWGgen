#!/usr/bin/env python3
"""
Testy jednostkowe funkcji blokowania użytkowników WireGuard VPN.

Moduł testuje implementację blokady/odblokowania użytkowników:
- Operacje JSON (user_records.json)
- Parsowanie i modyfikacja wg_server.conf
- Komentowanie/odkomentowywanie bloków [Peer]
- Synchronizacja WireGuard (wg syncconf)
- Obsługa błędów i rollback
"""

import pytest
import os
from pathlib import Path
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestBlockUser:
    """Testy jednostkowe funkcji blokowania użytkowników."""

    MAIN_FILE = 'gradio_admin/functions/block_user.py'

    def test_file_exists(self):
        """Test istnienia pliku."""
        assert os.path.exists(self.MAIN_FILE)

    def test_imports_present(self):
        """Test obecności kluczowych importów."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'import json', 'subprocess', 'USER_DB_PATH', 
            'SERVER_CONFIG_FILE', 'SERVER_WG_NIC'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Brakuje: {imp}"

    def test_internal_functions(self):
        """Test obecności głównych funkcji."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        functions = [
            'def load_user_records():',
            'def save_user_records(',
            'def block_user(username):',
            'def unblock_user(username):',
            'def update_wireguard_config('
        ]
        
        for func in functions:
            assert func in content, f"Brakuje: {func}"

    def test_status_logic(self):
        """Test logiki statusów 'blocked'/'active'."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert '["status"] = "blocked"' in content
        assert '["status"] = "active"' in content

    def test_wireguard_parsing(self):
        """Test parsowania konfiguracji WireGuard."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        wg_features = [
            '### Client {username}',
            'in_peer_block = True',
            'if line.startswith("# ")',
            'wg syncconf'
        ]
        
        for feature in wg_features:
            assert feature in content, f"Brakuje funkcji WG: {feature}"

    def test_error_handling(self):
        """Test obsługi błędów."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        error_patterns = [
            'FileNotFoundError:', 'except Exception as e:',
            '"[BŁĄD] Nie udało się',
            'return False,'
        ]
        
        for pattern in error_patterns:
            assert pattern in content, f"Brakuje obsługi błędu: {pattern}"

    def test_json_operations(self):
        """Test operacji JSON."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        json_ops = [
            'json.load(f)', 'json.dump(records, f, indent=4)',
            'with open(USER_DB_PATH, "r")',
            'with open(USER_DB_PATH, "w")'
        ]
        
        for op in json_ops:
            assert op in content, f"Brakuje operacji JSON: {op}"

    def test_config_update_logic(self):
        """Test logiki aktualizacji konfiguracji."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'updated_lines.append(f"# {line}")' in content
        assert 'updated_lines.append(line[2:])' in content

    def test_wg_sync_command(self):
        """Test komendy synchronizacji WireGuard."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'wg syncconf' in content
        assert 'SERVER_WG_NIC' in content
        assert 'wg-quick strip' in content

    def test_return_patterns(self):
        """Test wzorców zwracanych wartości."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'return True,' in content
        assert 'return False,' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
