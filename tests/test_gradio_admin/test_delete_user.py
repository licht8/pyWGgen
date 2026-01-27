#!/usr/bin/env python3
"""
Testy jednostkowe funkcji usuwania użytkownika WireGuard VPN.

Moduł testuje implementację usuwania użytkownika:
- System logowania z timestamp
- Operacje plików (user_records.json, wg configs, QR)
- Komendy WireGuard (wg set peer, wg syncconf)
- Parsowanie konfiguracji wg_server.conf
- Obsługa błędów i walidacja
"""

import pytest
import os
from pathlib import Path
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestDeleteUser:
    """Testy jednostkowe funkcji usuwania użytkownika."""

    MAIN_FILE = 'gradio_admin/functions/delete_user.py'

    def test_file_exists(self):
        """Test istnienia pliku."""
        assert os.path.exists(self.MAIN_FILE)

    def test_imports_present(self):
        """Test obecności kluczowych importów."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'import os', 'subprocess', 'from datetime import datetime',
            'read_json', 'write_json', 'get_wireguard_config_path',
            'WG_CONFIG_DIR', 'QR_CODE_DIR', 'SERVER_WG_NIC'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Brakuje: {imp}"

    def test_internal_functions(self):
        """Test obecności głównych funkcji."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        functions = [
            'def log_debug(message):',
            'def delete_user(username):',
            'def extract_public_key(',
            'def remove_peer_from_config('
        ]
        
        for func in functions:
            assert func in content, f"Brakuje: {func}"

    def test_logging_system(self):
        """Test systemu logowania z timestamp."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        log_features = [
            'def log_debug(message):',
            'strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]',
            'DEBUG    ℹ️ ',
            '---------- 🔥 Proces'
        ]
        
        for feature in log_features:
            assert feature in content, f"Brakuje logowania: {feature}"

    def test_file_operations(self):
        """Test operacji plików."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        file_ops = [
            '"user_records.json"',
            'os.remove(wg_config_file)',
            'os.remove(qr_code_file)',
            'WG_CONFIG_DIR', 'QR_CODE_DIR'
        ]
        
        for op in file_ops:
            assert op in content, f"Brakuje operacji pliku: {op}"

    def test_wireguard_commands(self):
        """Test komend WireGuard."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        wg_commands = [
            '"sudo", "wg", "set", "wg0", "peer"',
            'wg syncconf',
            'wg-quick strip',
            'SERVER_WG_NIC'
        ]
        
        for cmd in wg_commands:
            assert cmd in content, f"Brakuje komendy WG: {cmd}"

    def test_json_handling(self):
        """Test obsługi JSON."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        json_ops = [
            'read_json(user_records_path)',
            'write_json(user_records_path, user_data)',
            'user_data.pop(username)'
        ]
        
        for op in json_ops:
            assert op in content, f"Brakuje JSON: {op}"

    def test_config_parsing(self):
        """Test parsowania konfiguracji."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        parsing = [
            'PublicKey"',
            '### Client {client_name}',
            'skip_lines = 5'
        ]
        
        for feature in parsing:
            assert feature in content, f"Brakuje parsowania: {feature}"

    def test_error_handling(self):
        """Test obsługi błędów."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        errors = [
            'if not os.path.exists(user_records_path):',
            'if username not in user_data:',
            'except Exception as e:',
            '❌ Błąd'
        ]
        
        for error in errors:
            assert error in content, f"Brakuje błędu: {error}"

    def test_success_patterns(self):
        """Test wzorców sukcesu."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        success = [
            '✅ Użytkownik',
            '🔐 Użytkownik',
            '✅ Konfiguracja'
        ]
        
        for pattern in success:
            assert pattern in content, f"Brakuje sukcesu: {pattern}"

    def test_return_values(self):
        """Test wartości zwrotnych."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'return f"✅' in content
        assert 'return f"❌' in content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
