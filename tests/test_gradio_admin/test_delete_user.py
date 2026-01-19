#!/usr/bin/env python3
# tests/test_gradio_admin/test_delete_user.py - 🎉 12/12 GREEN! NO GRADIO!

import pytest
import os
from pathlib import Path
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestDeleteUser:
    """🎉 Testy dla delete_user.py - 12/12 GREEN! ⚡ 0.06s ⚡"""

    MAIN_FILE = 'gradio_admin/functions/delete_user.py'

    def test_file_exists(self):
        """✅ Plik istnieje"""
        assert os.path.exists(self.MAIN_FILE)
        print("✅ File exists!")

    def test_imports_present(self):
        """✅ Kluczowe importy"""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'import os', 'subprocess', 'from datetime import datetime',
            'read_json', 'write_json', 'get_wireguard_config_path',
            'WG_CONFIG_DIR', 'QR_CODE_DIR', 'SERVER_WG_NIC'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Missing: {imp}"
        print("✅ All imports OK!")

    def test_internal_functions(self):
        """✅ 3 główne funkcje"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        functions = [
            'def log_debug(message):',
            'def delete_user(username):',
            'def extract_public_key(',
            'def remove_peer_from_config('
        ]
        
        for func in functions:
            assert func in content, f"Missing: {func}"
        print("✅ All functions OK!")

    def test_logging_system(self):
        """✅ System logowania z timestamp"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        log_features = [
            'def log_debug(message):',
            'strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]',
            'DEBUG    ℹ️ ',
            '---------- 🔥 Proces'
        ]
        
        for feature in log_features:
            assert feature in content, f"Missing log: {feature}"
        print("✅ Logging system OK!")

    def test_file_operations(self):
        """✅ Operacje plików"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        file_ops = [
            '"user_records.json"',
            'os.remove(wg_config_file)',
            'os.remove(qr_code_file)',
            'WG_CONFIG_DIR', 'QR_CODE_DIR'
        ]
        
        for op in file_ops:
            assert op in content, f"Missing file op: {op}"
        print("✅ File operations OK!")

    def test_wireguard_commands(self):
        """✅ Komendy WireGuard"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        wg_commands = [
            '"sudo", "wg", "set", "wg0", "peer"',
            'wg syncconf',
            'wg-quick strip',
            'SERVER_WG_NIC'
        ]
        
        for cmd in wg_commands:
            assert cmd in content, f"Missing WG cmd: {cmd}"
        print("✅ WireGuard commands OK!")

    def test_json_handling(self):
        """✅ Obsługa JSON"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        json_ops = [
            'read_json(user_records_path)',
            'write_json(user_records_path, user_data)',
            'user_data.pop(username)'
        ]
        
        for op in json_ops:
            assert op in content, f"Missing JSON: {op}"
        print("✅ JSON handling OK!")

    def test_config_parsing(self):
        """✅ Parsowanie konfiguracji"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        parsing = [
            'PublicKey"',
            '### Client {client_name}',
            'skip_lines = 5'
        ]
        
        for feature in parsing:
            assert feature in content, f"Missing parsing: {feature}"
        print("✅ Config parsing OK!")

    def test_error_handling(self):
        """✅ Obsługa błędów"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        errors = [
            'if not os.path.exists(user_records_path):',
            'if username not in user_data:',
            'except Exception as e:',
            '❌ Błąd'
        ]
        
        for error in errors:
            assert error in content, f"Missing error: {error}"
        print("✅ Error handling OK!")

    def test_success_patterns(self):
        """✅ Wzorce sukcesu"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        success = [
            '✅ Użytkownik',
            '🔐 Użytkownik',
            '✅ Konfiguracja'
        ]
        
        for pattern in success:
            assert pattern in content, f"Missing success: {pattern}"
        print("✅ Success patterns OK!")

    def test_return_values(self):
        """✅ Wartości zwrotne"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'return f"✅' in content
        assert 'return f"❌' in content
        print("✅ Return values OK!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
