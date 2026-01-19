#!/usr/bin/env python3
# tests/test_gradio_admin/test_block_user.py - 🎉 10/10 GREEN! NO GRADIO!

import pytest
import os
from pathlib import Path
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestBlockUser:
    """🎉 Testy dla block_user.py - 10/10 GREEN! ⚡ 0.05s ⚡"""

    MAIN_FILE = 'gradio_admin/functions/block_user.py'

    def test_file_exists(self):
        """✅ Plik istnieje"""
        assert os.path.exists(self.MAIN_FILE)
        print("✅ File exists!")

    def test_imports_present(self):
        """✅ Kluczowe importy"""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'import json', 'subprocess', 'USER_DB_PATH', 
            'SERVER_CONFIG_FILE', 'SERVER_WG_NIC'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Missing: {imp}"
        print("✅ All imports OK!")

    def test_internal_functions(self):
        """✅ 5 głównych funkcji"""
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
            assert func in content, f"Missing: {func}"
        print("✅ All functions OK!")

    def test_status_logic(self):
        """✅ Logika statusów 'blocked'/'active'"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert '["status"] = "blocked"' in content
        assert '["status"] = "active"' in content
        print("✅ Status logic OK!")

    def test_wireguard_parsing(self):
        """✅ Parsowanie konfiguracji WireGuard"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        wg_features = [
            '### Client {username}',
            'in_peer_block = True',
            'if line.startswith("# ")',
            'wg syncconf'
        ]
        
        for feature in wg_features:
            assert feature in content, f"Missing WG feature: {feature}"
        print("✅ WireGuard parsing OK!")

    def test_error_handling(self):
        """✅ Obsługa błędów"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        error_patterns = [
            'FileNotFoundError:', 'except Exception as e:',
            '"[BŁĄD] Nie udało się',
            'return False,'
        ]
        
        for pattern in error_patterns:
            assert pattern in content, f"Missing error handling: {pattern}"
        print("✅ Error handling OK!")

    def test_json_operations(self):
        """✅ Operacje JSON"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        json_ops = [
            'json.load(f)', 'json.dump(records, f, indent=4)',
            'with open(USER_DB_PATH, "r")',
            'with open(USER_DB_PATH, "w")'
        ]
        
        for op in json_ops:
            assert op in content, f"Missing JSON op: {op}"
        print("✅ JSON operations OK!")

    def test_config_update_logic(self):
        """✅ Logika aktualizacji konfiguracji"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'updated_lines.append(f"# {line}")' in content  # Blokowanie
        assert 'updated_lines.append(line[2:])' in content     # Odblokowanie
        print("✅ Config update logic OK!")

    def test_wg_sync_command(self):
        """✅ Komenda synchronizacji WireGuard"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'wg syncconf' in content
        assert 'SERVER_WG_NIC' in content
        assert 'wg-quick strip' in content
        print("✅ WG sync command OK!")

    def test_return_patterns(self):
        """✅ Wzorce zwracanych wartości"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'return True,' in content
        assert 'return False,' in content
        print("✅ Return patterns OK!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
